#!/usr/bin/python
#
# From params.c - sybase example program
#
# Description:
#    This program uses ct_command with variables to query the
#    pubs2.dbo.titles table. It takes two INPUT parameters -
#        Parameter               Type
#        ---------               ----
#        type of book (type)     character
#        cost of book (price)    float
#
#    It then retrieves all title ids that cost more than or equal to
#    the input price for the input type of book.  It makes use of the
#    CS_FLOAT_TYPE for the 'price' variable, which corresponds to the
#    'C' language 'double' type.
#
# References:
#    Open Client/C Reference manual - check the pages for ct_command
#    and ct_param.
#
# Notes:
#    Also refer to the section on Data types to see how client types
#    are implemented.
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
    if cmd.ct_command(CS_LANG_CMD, sql) != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_connect failed')
    print
    print '*********************************************************'
    print 'This query will return all title ids for a given type of '
    print 'book that cost more \n than a given amount.'
    print '*********************************************************'
    print 'business'
    print 'mod_cook'
    print 'popular_comp'
    print 'psychology'
    print 'trad_cook'
    print 'UNDECIDED'
    type = raw_input('\nPlease choose one of the book types listed above: ')
    # Define the first input parameter of type character.
    buf1 = DataBuf(type)
    buf1.name = '@type'
    buf1.status = CS_INPUTVALUE
    if cmd.ct_param(buf1)  != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_param failed')
    # Define the second input parameter which is of type integer. 
    price = float(raw_input('Enter the cut-off price for the books: '))
    buf2 = DataBuf(price)
    buf2.name = '@price'
    buf2.status = CS_INPUTVALUE
    if cmd.ct_param(buf2) != CS_SUCCEED:
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

    print 'Title id       Type             Price'
    print '--------       ----             -----'
    # Fetch the bound data into host variables
    while 1:
        status, rows_read = cmd.ct_fetch()
        if status not in (CS_SUCCEED, CS_ROW_FAIL):
            break
        if status == CS_ROW_FAIL:
            print 'ct_fetch returned row fail'
            continue
        for i in range(num_cols):
            print ' %s      ' % bufs[i][0],
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

# Allocate and initialize a context 
ctx = init_db()
# Open a connection to the server 
conn = connect_db(ctx, EX_USERNAME, EX_PASSWORD)
# Allocate a command structure 
status, cmd = conn.ct_cmd_alloc()
if status != CS_SUCCEED:
    raise CTError(conn, 'ct_cmd_alloc failed')
# send the command to the server 
send_sql(cmd,
         'select title_id, type, price from pubs2.dbo.titles' \
         ' where type = @type and price >= @price')
# Process results from the server 
handle_returns(cmd)
# Drop the command structure 
if cmd.ct_cmd_drop() != CS_SUCCEED:
    raise CTError(conn, 'ct_cmd_drop failed')
# Close connection to the server 
status = conn.ct_close()
# Drop the context and do general cleanup 
cleanup_db(ctx, status)
print '\n End of program run!'
