#!/usr/bin/python
#
# From dynamic_ins.c - sybase example program
#
# Description:
#    This program uses Dynamic SQL to insert values into a table x
#    number of times. The insert statement, which contains
#    placeholders with identifiers, is sent to the server to be
#    partially compiled and stored. Therefore, every time you call the
#    insert routine, you are in effect only passing new values for the
#    insert (parameters to the temporary stored procs).
#
# Script file:
#    dynamic_ins.sql is included at the end of this file.
#
# References:
#    Open Client-Library/C Reference Manual. Refer to the sections on
#    Dynamic SQL and ct_dynamic.
#
# Note:
#    Dynamic SQL is mainly intended for precompiler support.
#
import sys
from sybasect import *
from example import *

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
            print 'TYPE: CMD DONE'
        elif result == CS_CMD_FAIL:
            raise CTError(cmd.conn, 'ct_results: CS_CMD_FAIL')
        elif result == CS_PARAM_RESULT:
            print 'TYPE: PARAM RESULT'
        elif result == CS_STATUS_RESULT:
            print 'TYPE: STATUS RESULTS'
        elif result == CS_COMPUTE_RESULT:
            print 'TYPE: COMPUTE RESULTS'
        else:
            sys.stderr.write('unknown results\n')
            return
    if status != CS_END_RESULTS:
        raise CTError(cmd.conn, 'ct_results failed')

def do_dynamic_insert(cmd, insert_statement, repeat_count):
    # prepare the dynamic statement
    if cmd.ct_dynamic(CS_PREPARE, 'd_insert', insert_statement) != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_dynamic CS_PREPARE failed')
    if cmd.ct_send() != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_send failed')
    handle_returns(cmd)
    # loop the requested number of times prompting for parameters and
    # sending actual values to server
    for i in range(repeat_count):
        col1 = raw_input('Enter value for col1 ( int ) ')
        col2 = raw_input('Enter value for col2 ( char )')
        # Execute phase of the dynamic statement
        if cmd.ct_dynamic(CS_EXECUTE, 'd_insert') != CS_SUCCEED:
            raise CTError(cmd.conn, 'ct_dynamic CS_EXECUTE failed')
        # prepare the first parameter description
        buf1 = DataBuf(int(col1))
        buf1.status = CS_INPUTVALUE
        # set up the first paramenter
        if cmd.ct_param(buf1) != CS_SUCCEED:
            raise CTError(cmd.conn, 'ct_param failed')
        # prepare the second parameter description
        buf2 = DataBuf(col2)
        buf2.status = CS_INPUTVALUE
        # set up the second paramenter
        if cmd.ct_param(buf2) != CS_SUCCEED:
            raise CTError(cmd.conn, 'ct_param failed')
        # send the parameter packet to server
        if cmd.ct_send() != CS_SUCCEED:
            raise CTError(cmd.conn, 'ct_send failed')
        handle_returns(cmd)
    # clean up the dynamic insert
    if cmd.ct_dynamic(CS_DEALLOC, 'd_insert') != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_dynamic CS_DEALLOC failed')
    if cmd.ct_send() != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_send failed')
    handle_returns(cmd)

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

# setup context of database connections
ctx = init_db()
# connect to SQL Server	
conn = connect_db(ctx, EX_USERNAME, EX_PASSWORD)
# alloc a command struct (controls SQL sent)
status, cmd = conn.ct_cmd_alloc()
if status != CS_SUCCEED:
    raise CTError(conn, 'ct_cmd_alloc failed')
# send a dynamic insert to the server the ? marks are placeholders for
# values to be supplied latter The integer is the number of times to
# repeat the insert, in this case, 2.
do_dynamic_insert(cmd, 'insert tempdb..test values (? ,?)', 2)
# drop the command structure
if cmd.ct_cmd_drop() != CS_SUCCEED:
    raise CTError(conn, 'ct_cmd_drop failed')
# close the connection to the server
status = conn.ct_close()
cleanup_db(ctx, status)
print 'End of program run!'
