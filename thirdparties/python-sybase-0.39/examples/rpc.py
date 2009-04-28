#!/usr/bin/python
#
# From rpc.c - sybase example program
#
# Description:
#    This program uses RPC calls to execute a pre-defined stored
#    procedure (see rpc.sql). This stored procedure accepts two INPUT
#    parameters:
#        Parameter		Type
#        ---------		----
#        book type 		character
#        total sales		integer
#    It then returns the number of books of the input 'type' that have
#    a 'total sales' of the input value or more.
#
# References:
#    Open Client/C Reference manual - check the pages for ct_command
#    and ct_param.
#
# Script file:
#    rpc.sql 
#
import sys
from sybasect import *
from example import *

MAX_COLSIZE = 255

def init_db():
    # allocate a context
    status, ctx = cs_ctx_alloc(CS_VERSION_100)
    if status != CS_SUCCEED:
        raise Error('cs_ctx_alloc failed')
    set_global_ctx(ctx)
    if ctx.cs_diag(CS_INIT) != CS_SUCCEED:
        raise CSError(ctx, 'cs_diag failed')
    # initialize the library
    if ctx.ct_init(CS_VERSION_100) != CS_SUCCEED:
        raise CSError(ctx, 'ct_init failed')
    return ctx

def connect_db(ctx, user_name, password):
    # Allocate a connection pointer
    status, conn = ctx.ct_con_alloc()
    if status != CS_SUCCEED:
        raise CSError(ctx, 'ct_con_alloc failed')
    if conn.ct_diag(CS_INIT) != CS_SUCCEED:
        raise CTError(conn, 'ct_diag failed')
    # Set the username and password properties
    if conn.ct_con_props(CS_SET, CS_USERNAME, user_name) != CS_SUCCEED:
        raise CTError(conn, 'ct_con_props CS_USERNAME failed')
    if conn.ct_con_props(CS_SET, CS_PASSWORD, password) != CS_SUCCEED:
        raise CTError(conn, 'ct_con_props CS_PASSWORD failed')
    # connect to the server
    if conn.ct_connect() != CS_SUCCEED:
        raise CTError(conn, 'ct_connect failed')
    return conn

def send_sql(cmd, sql):
    # Build and send the command to the server 
    if cmd.ct_command(CS_RPC_CMD, sql, CS_NO_RECOMPILE) != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_connect failed')
    type = raw_input('Please enter the type of book: ')
    # Define the first input parameter of type character.
    buf1 = DataBuf(type)
    buf1.name = '@type'
    buf1.status = CS_INPUTVALUE
    if cmd.ct_param(buf1)  != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_param failed')
    # Define the second input parameter which is of type integer. 
    tot_sales = raw_input('Enter the cut-off sales value: ')
    buf2 = DataBuf(int(tot_sales))
    buf2.name = '@tot_sales'
    buf2.status = CS_INPUTVALUE
    if cmd.ct_param(buf2) != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_param failed')
    # Define the output parameter now.
    buf3 = DataBuf(1)
    buf3.name = '@num_books'
    buf3.status = CS_RETURN
    if cmd.ct_param(buf3) != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_param failed')
    if cmd.ct_send() != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_send failed')

def bind_columns(cmd):
    status, num_cols = cmd.ct_res_info(CS_NUMDATA)
    if status != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_res_info failed')

    bufs = [None] * num_cols
    for i in range(num_cols):
        fmt = CS_DATAFMT()
        fmt.datatype = CS_CHAR_TYPE
        fmt.maxlength = MAX_COLSIZE
        fmt.count = 1
        fmt.format = CS_FMT_NULLTERM
        # Bind returned data to host variables
        status, buf = cmd.ct_bind(i + 1, fmt)
        if status != CS_SUCCEED:
            raise CTError(cmd.conn, 'ct_bind failed')
        bufs[i] = buf
    return bufs

def fetch_n_print(cmd, bufs):
    status, num_cols = cmd.ct_res_info(CS_NUMDATA)
    if status != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_res_info failed')

    # Fetch the bound data into host variables
    while 1:
        status, rows_read = cmd.ct_fetch()
        if status not in (CS_SUCCEED, CS_ROW_FAIL):
            break
        if status == CS_ROW_FAIL:
            print 'ct_fetch returned row fail'
            continue
        for i in range(num_cols):
            print ' Results: %s \t ' % bufs[i][0],
        print
    if status != CS_END_DATA:
        raise CTError(cmd.conn, 'ct_fetch failed')

def handle_returns(cmd):
    # Process all returned result types
    while 1:
        status, result = cmd.ct_results()
        if status != CS_SUCCEED:
            break
        if result == CS_ROW_RESULT:
            print 'TYPE: ROW RESULT'
            bufs = bind_columns(cmd)
            fetch_n_print(cmd, bufs)
        elif result == CS_CMD_SUCCEED:    
            print 'TYPE: CMD SUCCEEDED'
        elif result == CS_CMD_DONE:
            print 'TYPE : CMD DONE'
        elif result == CS_CMD_FAIL:
            raise CTError(cmd.conn, 'ct_results: CS_CMD_FAIL')
        elif result == CS_PARAM_RESULT:
            print 'TYPE: PARAM RESULT'
            bufs = bind_columns(cmd)
            fetch_n_print(cmd, bufs)
        elif result == CS_STATUS_RESULT:
            print 'TYPE: STATUS RESULTS'
            bufs = bind_columns(cmd)
            fetch_n_print(cmd, bufs)
        elif result == CS_COMPUTE_RESULT:
            print 'TYPE: COMPUTE RESULTS'
        else:
            sys.stderr.write('unknown results\n')
            return
    if status != CS_END_RESULTS:
        raise CTError(cmd.conn, 'ct_results failed')

def cleanup_db(ctx, status):
    if status != CS_SUCCEED:
        exit_type = CS_FORCE_EXIT
    else:
        exit_type = CS_UNUSED
    # close and cleanup connection to the server
    if ctx.ct_exit(exit_type) != CS_SUCCEED:
        raise CSError(ctx, 'ct_exit failed')
    # drop the context
    if ctx.cs_ctx_drop() != CS_SUCCEED:
        raise CSError(ctx, 'cs_ctx_drop failed')

# Allocate a context and initialize client-library 
ctx = init_db()
# Establish a connection to the server 
conn = connect_db(ctx, EX_USERNAME, EX_PASSWORD)
# Allocate a command structure 
status, cmd = conn.ct_cmd_alloc()
if status != CS_SUCCEED:
    raise CTError(conn, 'ct_cmd_alloc failed')
# Send the command to execute the rpc to the server 
send_sql(cmd, 'tempdb..test_proc')
# Process results from the server 
handle_returns(cmd)
# Drop the command structure 
if cmd.ct_cmd_drop() != CS_SUCCEED:
    raise CTError(conn, 'ct_cmd_drop failed')
# Close the connection to the server 
status = conn.ct_close()
# Drop the context and do general cleanup 
cleanup_db(ctx, status)
print '\n End of program run!'
