#!/usr/bin/python
#
# From array_bind.c - sybase example program
#
# Description:
#    This program uses bulk library calls to bulk copy variable and
#    fixed length data using array binding.  Array binding variable
#    length data is different from handling fixed length data. Please
#    read the sections in the 'References' below for a detailed
#    explanation.  Array binding helps improve performance.
#
# Script file:
#    Execute script array_bind.sql prior to executing the program.
# 
# Note:
#    This program requires bulk-library 11.x and up, as it uses a new
#    api call 'blk_rowxfer_mult' available only in this release.
#
# References:
#    Open Client/Open Server Common Libraries reference manual.  Refer
#    to the sections on 'blk_rowxfer_mult' and 'Array Binding'.
#
import sys
import string
from sybasect import *
from example import *

def init_db():
    status, ctx = cs_ctx_alloc(CS_VERSION_100)
    if status != CS_SUCCEED:
        raise Error('cs_ctx_alloc failed')
    set_global_ctx(ctx)
    if ctx.cs_diag(CS_INIT) != CS_SUCCEED:
        raise CSError(ctx, 'cs_diag failed')
    status = ctx.ct_init(CS_VERSION_100)
    if status != CS_SUCCEED:
        raise CSError(ctx, 'ct_init failed')
    return ctx

def connect_db(ctx, user_name, password):
    status, conn = ctx.ct_con_alloc()
    if status != CS_SUCCEED:
        raise CSError(ctx, 'ct_con_alloc failed')
    if conn.ct_diag(CS_INIT) != CS_SUCCEED:
        raise CTError('ct_diag failed')
    if conn.ct_con_props(CS_SET, CS_USERNAME, user_name) != CS_SUCCEED:
        raise CTError(conn, 'ct_con_props CS_USERNAME failed')
    if conn.ct_con_props(CS_SET, CS_PASSWORD, password) != CS_SUCCEED:
        raise CTError(conn, 'ct_con_props CS_PASSWORD failed')
    if conn.ct_con_props(CS_SET, CS_BULK_LOGIN, CS_TRUE) != CS_SUCCEED:
        raise CTError(conn, 'ct_con_props CS_BULK_LOGIN failed')
    if conn.ct_connect() != CS_SUCCEED:
        raise CTError(conn, 'ct_connect failed')
    return conn

def send_sql(cmd, sql):
    print 'sql = %s' % sql
    if cmd.ct_command(CS_LANG_CMD, sql) != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_command failed')
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
        fmt.maxlength = 255
        fmt.count = 1
        fmt.format = CS_FMT_NULLTERM
        status, buf = cmd.ct_bind(i + 1, fmt)
        if status != CS_SUCCEED:
            raise CTError(cmd.conn, 'ct_bind failed')
        bufs[i] = buf
    return bufs

def fetch_n_print(cmd, bufs):
    status, num_cols = cmd.ct_res_info(CS_NUMDATA)
    if status != CS_SUCCEED:
        raise CTError(cmd.conn, 'ct_res_info failed')

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
        else:
            sys.stderr.write('unknown results\n')
            return
    if status == CS_END_RESULTS:
        return CS_SUCCEED
    raise CTError(cmd.conn, 'ct_results failed')

def write_to_table(conn, data):
    status, blk = conn.blk_alloc(BLK_VERSION_110)
    if status != CS_SUCCEED:
        raise CSError(conn.ctx, 'blk_alloc failed')
    if blk.blk_init(CS_BLK_IN, 'test_bcp') != CS_SUCCEED:
        raise CSError(conn.ctx, 'blk_init failed')

    int_fmt = CS_DATAFMT()
    int_fmt.count = len(data[0])
    int_fmt.datatype = CS_INT_TYPE
    int_fmt.format = CS_FMT_UNUSED
    int_fmt.maxlength = sizeof_type(CS_INT_TYPE)
    int_buf = DataBuf(int_fmt)
    for i in range(len(data[0])):
        int_buf[i] = data[0][i]
    if blk.blk_bind(1, int_buf) != CS_SUCCEED:
        raise CSError(conn.ctx, 'blk_bind failed')
    # Initialize and describe the data format structure for the second
    # column of type 'char'. It is recommended that different data
    # format structures be used for different datatypes.
    char_fmt = CS_DATAFMT()
    char_fmt.count = len(data[1])
    char_fmt.datatype = CS_CHAR_TYPE;
    char_fmt.format = CS_BLK_ARRAY_MAXLEN
    char_fmt.maxlength = 10
    # Since we have variable length data, specify the length of each
    # data value.
    char_buf = DataBuf(char_fmt)
    for i in range(len(data[1])):
        char_buf[i] = data[1][i]
    if blk.blk_bind(2, char_buf) != CS_SUCCEED:
        raise CSError(conn.ctx, 'blk_bind failed')
    # transfer the rows to be copied to the server
    status, row_count = blk.blk_rowxfer_mult(len(data[0]))
    if status != CS_SUCCEED:
        raise CSError(conn.ctx, 'blk_rowxfer_mult failed')
    # Commit transactions to the database 
    status, num_rows = blk.blk_done(CS_BLK_ALL)
    if status != CS_SUCCEED:
        raise CSError(conn.ctx, 'blk_done failed')
    print 'Bulk copied %d rows successfully.' % num_rows
    # Drop the bulk descriptor
    if blk.blk_drop() != CS_SUCCEED:
        raise CSError(conn.ctx, 'blk_done failed')

data = ((1001,1002,1003,1004,1005),
        ('Sandy', 'Mary', 'Joe', 'Smith', 'Jill'))

ctx = init_db()
conn = connect_db(ctx, EX_USERNAME, EX_PASSWORD)
status, cmd = conn.ct_cmd_alloc()
if status != CS_SUCCEED:
    raise CTError(conn, 'ct_cmd_alloc failed')
send_sql(cmd, 'use tempdb')
handle_returns(cmd)
write_to_table(conn, data)
# Now select the data back from the table, so we can see what we
# inserted.
send_sql(cmd, 'select * from test_bcp ')
# handle results from the current command
handle_returns(cmd)
# Drop the command structure 
print '\n End of bulkcopy program.'

