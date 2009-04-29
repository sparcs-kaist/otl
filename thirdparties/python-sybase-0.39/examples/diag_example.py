#!/usr/bin/python
#
# From diag_example.c - sybase example program
#
# Description:
#    This program accepts a SQL statement from the user and uses
#    ct_diag to report error messages.  The routine 'call_diag' is
#    called every time you make a call that could generate a error.
#
# Tests to try: 
# (1) To test server messages, issue an invalid SQL statement such as
#     select * from a non-existent table
# (2) To test client-library messages, set the datatype for the bind
#     to a datatype different from the expected results. (Change
#     datafmt.datatype).
#
# References:
#    Open Client-Library/C Reference Manual. Refer to the sections
#    on Inline error handling and ct_diag.
#
import sys
from sybasect import *
from example import *

def send_sql(cmd, sql):
    print 'SQL = %s' % sql
    # Build and send the command to the server
    if cmd.ct_command(CS_LANG_CMD, sql) == CS_SUCCEED:
        cmd.ct_send()

def print_ClientMsg(msg):
    sys.stderr.write('\nNumber: layer (%ld), Origin (%ld) \ntext%s\n' \
                     % (CS_LAYER(msg.msgnumber), CS_ORIGIN(msg.msgnumber),
                        msg.msgstring))
    sys.stderr.write('SEVERITY = (%ld) NUMBER = (%ld)\n' \
                     % (CS_SEVERITY(msg.msgnumber), CS_NUMBER(msg.msgnumber)))
    sys.stderr.write('Message String: %s\n' % msg.msgstring)
    if msg.osstringlen:
        sys.stderr.write('\nOS error : %s\n' % msg.osstring)

def print_ServerMsg(msg):
    sys.stderr.write('\nServer message:\n')
    sys.stderr.write('Message number: %ld, Severity %ld, ' \
                     % (msg.msgnumber, msg.severity))
    sys.stderr.write('State %ld, Line %ld\n' % (msg.state, msg.line))
    if msg.svrname:
        sys.stderr.write("Server '%s'\n" % msg.svrname)
    if msg.proc:
        sys.stderr.write(" Procedure '%s'\n" % msg.proc)
    sys.stderr.write('Message String: %s\n' % msg.text)

def call_diag(conn):
    # Check to see if there are any messages in the CS_CLIENTMSG structure
    status, num_msgs = conn.ct_diag(CS_STATUS, CS_CLIENTMSG_TYPE)
    if status == CS_SUCCEED:
        for i in range(num_msgs):
            status, msg = conn.ct_diag(CS_GET, CS_CLIENTMSG_TYPE, i + 1)
            if status != CS_SUCCEED:
                return
            print_ClientMsg(msg);
    # Check to see if there are any messages in the CS_SERVERMSG structure
    status, num_msgs = conn.ct_diag(CS_STATUS, CS_SERVERMSG_TYPE)
    if status == CS_SUCCEED:
        for i in range(num_msgs):
            status, msg = conn.ct_diag(CS_GET, CS_SERVERMSG_TYPE, i + 1)
            if status != CS_SUCCEED:
                return
            print_ServerMsg(msg)
    # Clear the structures of existing error messages
    conn.ct_diag(CS_CLEAR, CS_SERVERMSG_TYPE)
    conn.ct_diag(CS_CLEAR, CS_CLIENTMSG_TYPE)

def bind_columns(cmd):
    status, num_cols = cmd.ct_res_info(CS_NUMDATA)
    if status != CS_SUCCEED:
        sys.stderr.write('ct_res_info failed\n')
        return status, None
    bufs = [None] * num_cols
    for i in range(num_cols):
        fmt = CS_DATAFMT()
        fmt.datatype = CS_CHAR_TYPE
        fmt.maxlength = 255 
        fmt.count = 1
        fmt.format = CS_FMT_NULLTERM
        # Bind returned data to host variables
        status, buf = cmd.ct_bind(i + 1, fmt)
        if status != CS_SUCCEED:
            sys.stderr.write('ct_bind failed\n')
            return status, None
        bufs[i] = buf
    return CS_SUCCEED, bufs

def fetch_n_print(cmd, bufs):
    status, num_cols = cmd.ct_res_info(CS_NUMDATA)
    if status != CS_SUCCEED:
        sys.stderr.write('ct_res_info failed\n')
        return status
    # Fetch the bound data into host variables
    while 1:
        status, rows_read = cmd.ct_fetch()
        if status not in (CS_SUCCEED, CS_ROW_FAIL):
            break
        if status == CS_ROW_FAIL:
            print 'ct_fetch returned row fail'
            continue
        for i in range(num_cols):
            print ' %s \t' % bufs[i][0],
        print
    # Check to see that all rows have been fetched
    if status != CS_END_DATA:
        sys.stderr.write('ct_fetch failed\n')
        return status
    return CS_SUCCEED

def handle_returns(cmd):
    # Process all returned result types
    while 1:
        status, result = cmd.ct_results()
        if status != CS_SUCCEED:
            break
        if result == CS_ROW_RESULT:
            print 'TYPE: ROW RESULT'
            status, bufs = bind_columns(cmd)
            if status != CS_SUCCEED:
                sys.stderr.write('bind_columns failed\n')
                return
            if fetch_n_print(cmd, bufs) != CS_SUCCEED:
                sys.stderr.write('fetch_n_print failed\n')
                return
        elif result == CS_CMD_SUCCEED:	
            print 'TYPE: CMD SUCCEEDED'
        elif result == CS_CMD_DONE:
            print 'TYPE : CMD DONE'
        elif result == CS_CMD_FAIL:
            print 'TYPE: CMD FAIL'
        elif result == CS_STATUS_RESULT:
            print 'TYPE: STATUS RESULTS'
            status, bufs = bind_columns(cmd)
            if status != CS_SUCCEED:
                sys.stderr.write('bind_columns failed\n')
                return
            if fetch_n_print(cmd, bufs) != CS_SUCCEED:
                sys.stderr.write('fetch_n_print failed\n')
                return
        elif result == CS_CURSOR_RESULT:
            printf('TYPE: CURSOR RESULT \n');
            status, bufs = bind_columns(cmd)
            if status != CS_SUCCEED:
                sys.stderr.write('bind_columns failed\n')
                return
            if fetch_n_print(cmd, bufs) != CS_SUCCEED:
                sys.stderr.write('fetch_n_print failed\n')
                return
        else:
            sys.stderr.write('unknown results\n')
            break

# Get a context structure
status, ctx = cs_ctx_alloc(EX_CTLIB_VERSION)
if status != CS_SUCCEED:
    raise Error('cs_ctx_alloc failed')
set_global_ctx(ctx)
# Initialize client library	
if ctx.ct_init(EX_CTLIB_VERSION) != CS_SUCCEED:
    raise CSError(ctx, 'ct_init failed')
# Allocate a connection pointer
status, conn = ctx.ct_con_alloc()
if status != CS_SUCCEED:
    raise CSError(ctx, 'ct_con_alloc failed')
# Set the username and password properties
if conn.ct_con_props(CS_SET, CS_USERNAME, EX_USERNAME) != CS_SUCCEED:
    raise CTError(conn, 'ct_con_props CS_USERNAME failed')
if conn.ct_con_props(CS_SET, CS_PASSWORD, EX_PASSWORD) != CS_SUCCEED:
    raise CTError(conn, 'ct_con_props CS_PASSWORD failed')
# Establish a connection to the server    
if conn.ct_connect() != CS_SUCCEED:
    raise CTError(conn, 'ct_connect failed')
# Initialize inline error handling 
if conn.ct_diag(CS_INIT) != CS_SUCCEED:
    raise CTError(conn, 'ct_diag failed')
# Allocate a command structure  
status, cmd = conn.ct_cmd_alloc()
if status != CS_SUCCEED:
    raise CTError(conn, 'ct_cmd_alloc failed')
# Send a command to the server
sql = raw_input('Enter the SQL statement to execute: ')
send_sql(cmd, sql)
# check for errors
call_diag(conn)
call_diag(conn)
# handle results from previous command
handle_returns(cmd)
# check for errors
call_diag(conn)
# Close connection
if conn.ct_close( ) != CS_SUCCEED:
    raise CTError(conn, 'ct_close failed')
print 'End of program run!'
