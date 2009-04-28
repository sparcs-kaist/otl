#!/usr/bin/python
#
# From timeout.c - sybase example program
#
# Description:
#    This program handles timeout errors. It shows how a command that
#    has timed out can be cancelled and then returns results from the
#    next command on the same connection. It also shows how one
#    connection can be marked dead as a result of a timeout and still
#    return results from another connection.
#
# Usage:
#    Follow the instructions in the timeout.readme file to create a
#    timeout error.  Run this program in another window - a timeout
#    error will occur on the first command on the first connection.
#    You will be prompted to cancel only the current command that
#    caused a timeout and continue processing the following commands
#    on this connection as well as the next, or to wait for another
#    timeout period and see if the transaction goes through to
#    completion this time.
#
# References:
#    Open Client Client-Library/C Reference manual: refer to pages for
#    ct_config, ct_cancel and the section on 'Connection Status' under
#    Properties.
#
import sys
from sybasect import *

def ctlib_client_msg_handler(ctx, conn, msg):
    print "\nOPEN CLIENT ERROR MESSAGE"
    print "number: layer (%ld), origin (%ld)" \
          % (CS_LAYER(msg.msgnumber), CS_ORIGIN(msg.msgnumber))
    print "text:\n%s" % msg.msgstring
    if msg.osstring:
        print "OS error : %s" % msg.osstring
    # Handle timeout errors : 63 is 'Read from SQL Server timed out'.
    if CS_NUMBER(msg.msgnumber) == 63:
        print "\n"
        print "A TIMEOUT ERROR OCCURRED. Please choose "
        print "one of the following options:"
        print "1. Cancel only this command and continue processing."
        print "2. Continue to wait for another timeout period."
        ans = raw_input("\n Enter choice: ")
        if ans == '1':
            conn.ct_cancel(CS_CANCEL_ATTN)
            return CS_SUCCEED
        print "Waiting for another timeout period .."
    return CS_SUCCEED

def ctlib_server_msg_handler(ctx, conn, msg):
    # Suppress informational messages
    if msg.msgnumber not in (5701, 5703):
	print "\nSERVER MESSAGE"
        if msg.svrname:
            print " from server '%s'" % msg.svrname
	if msg.proc:
            print " at procedure '%s'" % msg.proc
        print "number (%ld), severity (%ld)" % (msg.msgnumber, msg.severity)
	print "state (%ld), line (%ld)" % (msg.state, msg.line)
	print "text:\n%s" % msg.text
	print "MESSAGE HANDLER OUTPUT ENDS"
    return CS_SUCCEED

EX_USERNAME = "sa"
EX_PASSWORD = ""

MAX_COLSIZE = 255

def exit_if(status, msg):
    if status != CS_SUCCEED:
        print 'error in %s' % msg
        sys.exit(1)

def bad_status(status, msg):
    if status != CS_SUCCEED:
        print 'error in %s' % msg
        return 1
    return 0

def init_db():
    # allocate a context
    status, ctx = cs_ctx_alloc(CS_VERSION_100)
    if bad_status(status, 'cs_ctx_alloc'):
        return status, None
    set_global_ctx(ctx)
    # initialize the library
    status = ctx.ct_init(CS_VERSION_100)
    bad_status(status, 'ct_init')
    return status, ctx

def connect_db(ctx, user_name, password):
    # Allocate a connection pointer
    status, conn = ctx.ct_con_alloc()
    if bad_status(status, 'ct_con_alloc'):
        return status, None
    # Set the username and password properties
    status = conn.ct_con_props(CS_SET, CS_USERNAME, user_name)
    if bad_status(status, 'ct_con_props'):
        return status, None
    status = conn.ct_con_props(CS_SET, CS_PASSWORD, password)
    if bad_status(status, 'ct_con_props'):
        return status, None
    status = ctx.ct_callback(CS_SET,
                             CS_SERVERMSG_CB, ctlib_server_msg_handler)
    if bad_status(status, 'ct_callback'):
        return status, None
    status = ctx.ct_callback(CS_SET,
                             CS_CLIENTMSG_CB, ctlib_client_msg_handler)
    if bad_status(status, 'ct_callback'):
        return status, None
    # connect to the server
    status = conn.ct_connect()
    return status, conn

def send_sql(cmd, sql):
    # Build and send the command to the server 
    status = cmd.ct_command(CS_LANG_CMD, sql)
    if bad_status(status, 'ct_command'):
        return status
    status = cmd.ct_send()
    bad_status(status, 'ct_send')
    return status

def bind_columns(cmd):
    status, num_cols = cmd.ct_res_info(CS_NUMDATA)
    if bad_status(status, 'ct_res_info'):
        return status, None
    bufs = [None] * num_cols
    for i in range(num_cols):
        fmt = CS_DATAFMT()
        fmt.datatype = CS_CHAR_TYPE
        fmt.maxlength = MAX_COLSIZE
        fmt.count = 1
        fmt.format = CS_FMT_NULLTERM
        # Bind returned data to host variables
        status, buf = cmd.ct_bind(i + 1, fmt)
        if bad_status(status, 'ct_bind'):
            return status, None
        bufs[i] = buf
    return status, bufs
 
def fetch_n_print(cmd, bufs):
    status, num_cols = cmd.ct_res_info(CS_NUMDATA)
    if bad_status(status, 'ct_res_info'):
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
            print ' %s \t ' % bufs[i][0],
        print
    if status != CS_END_DATA:
        bad_status(status, 'ct_fetch')
        return status
    return CS_SUCCEED

def handle_returns(cmd):
    # Process all returned result types
    while 1:
        status, result = cmd.ct_results()
        if status != CS_SUCCEED:
            break
        if result == CS_ROW_RESULT:
            status, bufs = bind_columns(cmd)
            if bad_status(status, 'bind_columns'):
                return status
            status = fetch_n_print(cmd, bufs)
            if bad_status(status, 'fetch_n_print'):
                return status
        elif result == CS_CMD_SUCCEED:    
            pass
        elif result == CS_CMD_DONE:
            pass
        elif result == CS_CMD_FAIL:
            print "TYPE: CMD_FAIL"
        elif result == CS_STATUS_RESULT:
            print 'TYPE: STATUS RESULTS'
        else:
            print "TYPE: UNKNOWN"
            bad_status(CS_FAIL, 'handle_returns')
            return CS_FAIL
    if status == CS_END_RESULTS:
        return CS_SUCCEED
    if status == CS_FAIL:
        print "ct_result returned:  CS_FAIL"
    return CS_FAIL

def cleanup_db(ctx):
    # close and cleanup connection to the server
    status = ctx.ct_exit()
    if bad_status(status, 'ct_exit'):
        return status
    # drop the context
    status = ctx.cs_ctx_drop()
    bad_status(status, 'cs_ctx_drop')
    return status

# Allocate context and initialize client-library 
status, ctx = init_db()
exit_if(status, 'init_db')
# Establish connections to the server 
status, conn1 = connect_db(ctx, EX_USERNAME, EX_PASSWORD)
exit_if(status, 'connect_db')
status, conn2 = connect_db(ctx, EX_USERNAME, EX_PASSWORD)
exit_if(status, 'connect_db')
# Allocate command structures on connection 1 
status, cmd1a = conn1.ct_cmd_alloc()
exit_if(status, 'ct_cmd_alloc')
status, cmd1b = conn1.ct_cmd_alloc()
exit_if(status, 'ct_cmd_alloc')
# Allocate a command structure on connection 2 
status, cmd2 = conn2.ct_cmd_alloc()
exit_if(status, 'ct_cmd_alloc')
# Set the timeout interval to 5 seconds.
timeout = 5
exit_if(ctx.ct_config(CS_SET, CS_TIMEOUT, timeout), 'ct_config')
print 'Timeout value = %d seconds' % timeout
# send sql text to server 	
print 'Executing Command 1 on connection 1..'
send_sql(cmd1a, 'select * from pubs2.dbo.publishers')
# process results 
handle_returns(cmd1a)
print 'Executing Command 2 on connection 1..'
send_sql(cmd1b, "select name from pubs2.dbo.sysobjects where type = 'U'")
handle_returns(cmd1b)
print 'Command 3 on connection 2..'
send_sql(cmd2, "select name from tempdb..sysobjects where type = 'U'")
handle_returns(cmd2)
# Drop all the command structures 
exit_if(cmd1a.ct_cmd_drop(), 'ct_cmd_drop')
exit_if(cmd1b.ct_cmd_drop(), 'ct_cmd_drop')
exit_if(cmd2.ct_cmd_drop(), 'ct_cmd_drop')
# Close the connections to the server 
exit_if(conn1.ct_close(), 'ct_close')
exit_if(conn2.ct_close(), 'ct_close')
# Drop context and do general cleanup 
cleanup_db(ctx)
print 'End of program run!'
