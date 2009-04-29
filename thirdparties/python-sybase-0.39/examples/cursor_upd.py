#!/usr/bin/python
#
# From cursor_upd.c - sybase example program
#
# Description:
#    This program uses a cursor to retrieve data from the publishers
#    table in the pubs2 database. It retrieves data row by row and
#    prompts the user to input new values for the column 'state' in
#    the publishers table.
#
# Inputs:
#    value for the input parameter ('state' column from the
#    'publishers' table ) for the UPDATE.
#
# Script File:
#    This program uses a copy of the publishers table (called
#    publishers2). Please run the script cursor_upd.sql before running
#    this program.
#
# References:
#    Open Client Reference Manual pages for ct_cursor and ct_param.

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

def single_row(cmd):
    state = raw_input('New state: ')
    if not len(state):
        # If the user hit 'enter' for the new input value, don't
        # bother updating.Return to the calling function.
        return
    sql = 'update pubs2.dbo.publishers2 set state = @state'
    if cmd.ct_cursor(CS_CURSOR_UPDATE,
                     'pubs2.dbo.publishers2', sql) != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_cursor CS_CURSOR_UPDATE failed')
    # Set up the parameters for the update
    buf = DataBuf(state)
    buf.name = '@state'
    buf.status = CS_INPUTVALUE;
    # If an input value was entered, do the update.
    if cmd.ct_param(buf) != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_param failed')
    if cmd.ct_send() != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_send failed')
    handle_returns(cmd)

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
            print ' %s \t' % bufs[i][0],
        print
        single_row(cmd)
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
        elif result == CS_CURSOR_RESULT:
            print 'TYPE: CURSOR RESULT'
            bufs = bind_columns(cmd)
            fetch_n_print(cmd, bufs)
        else:
            sys.stderr.write('unknown results\n')
            return
    if status != CS_END_RESULTS:
        raise CTError(cmd.conn, 'ct_results failed')

def open_cursor(cmd):
    if cmd.ct_cursor(CS_CURSOR_DECLARE,
                     'browse_cursor', 'select * from pubs2.dbo.publishers2',
                     CS_FOR_UPDATE) != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_cursor CS_CURSOR_DECLARE failed')
    if cmd.ct_cursor(CS_CURSOR_OPEN) != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_cursor CS_CURSOR_OPEN failed')
    if cmd.ct_send() != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_send failed')
    handle_returns(cmd)
    if cmd.ct_cursor(CS_CURSOR_CLOSE, CS_DEALLOC) != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_cursor CS_CURSOR_CLOSE failed')
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

# Allocate a context and initialize client-library
ctx = init_db()
# Establish a connection to the server
conn = connect_db(ctx, EX_USERNAME, EX_PASSWORD)
# Allocate a command structure
status, cmd = conn.ct_cmd_alloc()
if status != CS_SUCCEED:
    raise CTError(conn, 'ct_cmd_alloc failed')
# Perform cursor operations
open_cursor(cmd)
# Drop the command structure
if cmd.ct_cmd_drop() != CS_SUCCEED:
    raise CTError(conn, 'ct_cmd_drop failed')
# Close connection to the server
status = conn.ct_close()
# Drop the context and perform cleanup
cleanup_db(ctx, status)
print '\n End of program run!'
