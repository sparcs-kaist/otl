#!/usr/bin/python
#
# From dynamic_cur.c - sybase example program
#
# Description:
#    This program uses Dynamic SQL to retrieve values from the
#    'titles' table in the 'pubs2' database.  The select statement,
#    which contains placeholders with identifiers, is sent to the
#    server to be partially compiled and stored. Therefore, every time
#    you call the select, you in effect only pass new values for the
#    key value which determines the row to be retrieved.  The
#    behaviour is similar to passing input parameters to stored
#    procedures. The program also uses cursors to retrieve rows one by
#    one, which can be manipulated as required.
#
# References:
#    Open Client-Library/C reference manual. Refer to the sections on
#    Dynamic SQL , ct_dynamic and ct_cursor.
#
# Note:
#    Dynamic SQL is mainly intended for precompiler support.
#
import sys
from sybasect import *
from example import *

MAX_COLSIZE = 255

def init_db():
    # allocate a context
    status, ctx = cs_ctx_alloc(EX_CTLIB_VERSION)
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
            pass
        elif result == CS_CMD_DONE:
            pass
        elif result == CS_CMD_FAIL:
            raise CTError(cmd.conn, 'ct_results: CS_CMD_FAIL')
        elif result == CS_PARAM_RESULT:
            print 'TYPE: PARAM RESULT'
            bufs = bind_columns(cmd)
            fetch_n_print(cmd, bufs)
        elif result == CS_CURSOR_RESULT:
            print 'TYPE: CURSOR RESULT'
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

def open_cursor(cmd):
    # Prepare the sql statement for the first cursor 
    sql = 'select title_id, type, price from pubs2..titles where title_id = (?) '
    if cmd.ct_dynamic(CS_PREPARE, 'mycursor', sql) != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_dynamic CS_PREPARE failed')
    # Send the prepared statement to the server 
    if cmd.ct_send() != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_send failed')
    # See if the prepared statement was successful 
    handle_returns(cmd)
    # Declare a cursor for the prepared statement 
    if cmd.ct_dynamic(CS_CURSOR_DECLARE, 'mycursor', 'mycursor') != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_dynamic CS_CURSOR_DECLARE failed')
    # Set the cursor to read only 
    if cmd.ct_cursor(CS_CURSOR_OPTION, CS_READ_ONLY) != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_cursor CS_CURSOR_OPTION failed')
    # We need to get values for pub_id 
    print 'Enter title id value - enter an X if you wish to stop:'
    while 1:
	title_id = raw_input('Retrieve detail record for title id: ?')
        if not title_id or string.upper(title_id) == 'X':
            break
	# Open the cursor 
  	if cmd.ct_cursor(CS_CURSOR_OPEN) != CS_SUCCEED:
            raise CTError(cmd.conn, 'ct_cursor CS_CURSOR_OPEN failed')
	# Define the input parameter
        buf = DataBuf(title_id)
    	buf.status = CS_INPUTVALUE
        if cmd.ct_param(buf) != CS_SUCCEED:
            raise CTError(cmd.conn, 'ct_param failed') 
        # cursor open and params command
  	if cmd.ct_send() != CS_SUCCEED:
            raise CTError(cmd.conn, 'ct_send failed')
	handle_returns(cmd)
  	if cmd.ct_cursor(CS_CURSOR_CLOSE) != CS_SUCCEED:
            raise CTError(cmd.conn, 'ct_cursor CS_CURSOR_CLOSE failed')
   	if cmd.ct_send() != CS_SUCCEED:
            raise CTError(cmd.conn, 'ct_send failed')
   	handle_returns(cmd)
    # Now, deallocate the prepared statement 
    if cmd.ct_dynamic(CS_DEALLOC, 'mycursor') != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_dynamic CS_DEALLOC failed')
    # Send the dealloc statement to the server 
    if cmd.ct_send() != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_send failed')
    # process results from above commend 
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
# Begin cursor operations 
open_cursor(cmd)
# close the connection to the server 
status = conn.ct_close()
cleanup_db(ctx, status)
print 'Program completed successfully!'
