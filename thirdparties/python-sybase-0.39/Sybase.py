#
# Copyright 2001 by Object Craft P/L, Melbourne, Australia.
#
# LICENCE - see LICENCE file distributed with this software for details.
#
import sys
import time
import string
import threading
import copy
from sybasect import *
from sybasect import __have_freetds__
from sybasect import datetime as sybdatetime

set_debug(sys.stderr)

__version__ = '0.39'

# DB-API values
apilevel = '2.0'                        # DB API level supported

threadsafety = 2                        # Threads may share the module
                                        # and connections.


paramstyle = 'named'                    # Named style, 
                                        # e.g. '...WHERE name=@name'

use_datetime = 0                        # Deprecated: date type

# DB-API exceptions
#
# StandardError
# |__Warning
# |__Error
#    |__InterfaceError
#    |__DatabaseError
#       |__DataError
#       |__OperationalError
#       |__IntegrityError
#       |__InternalError
#       |__ProgrammingError
#       |__NotSupportedError

class Warning(StandardError):
    pass


class Error(StandardError):

    def append(self, other):
        self.args = (self.args[0] + other.args[0],)


class InterfaceError(Error):
    pass


class DatabaseError(Error):
    def __init__(self, msg):
        '''take a sybasect.CS_SERVERMSG so break out the fields for use'''
        if type(msg) == ServerMsgType:
            str = _fmt_server(msg)
        elif type(msg) == ClientMsgType:
            str = _fmt_client(msg)
        else:
            # Assume string
            str = msg
            msg = None
        Error.__init__(self, str)
        self.msg = msg
            
class DataError(DatabaseError):
    pass


class OperationalError(DatabaseError):
    pass


class IntegrityError(DatabaseError):
    pass


class InternalError(DatabaseError):
    pass


class ProgrammingError(DatabaseError):
    pass


class StoredProcedureError(ProgrammingError):
    pass


class NotSupportedError(DatabaseError):
    pass


class DBAPITypeObject:

    def __init__(self, *values):
	self.values = values

    def __cmp__(self, other):
	if other in self.values:
	    return 0
	if other < self.values:
	    return 1
	else:
	    return -1

    def __add__(self, other):
        values = self.values + other.values
        return DBAPITypeObject(*values)

try:
    _have_cs_date_type = DateType and CS_DATE_TYPE and True
except NameError:
    _have_cs_date_type = False

STRING = DBAPITypeObject(CS_LONGCHAR_TYPE, CS_VARCHAR_TYPE,
                         CS_TEXT_TYPE, CS_CHAR_TYPE)
BINARY = DBAPITypeObject(CS_IMAGE_TYPE, CS_LONGBINARY_TYPE,
                         CS_VARBINARY_TYPE, CS_BINARY_TYPE)
NUMBER = DBAPITypeObject(CS_BIT_TYPE, CS_TINYINT_TYPE,
                         CS_SMALLINT_TYPE, CS_INT_TYPE,
                         CS_MONEY_TYPE, CS_REAL_TYPE, CS_FLOAT_TYPE,
                         CS_DECIMAL_TYPE, CS_NUMERIC_TYPE)
DATETIME = DBAPITypeObject(DateTimeType, CS_DATETIME4_TYPE, CS_DATETIME_TYPE)
if _have_cs_date_type:
    DATETIME += DBAPITypeObject(DateType, CS_DATE_TYPE)
ROWID = DBAPITypeObject(CS_DECIMAL_TYPE, CS_NUMERIC_TYPE)


def OUTPUT(value):
    buf = DataBuf(value)
    buf.status = CS_RETURN
    return buf

def Date(year, month, day):
    return sybdatetime('%s-%s-%s' % (year, month, day))

def Time(hour, minute, second):
    return sybdatetime('%d:%d:%d' % (hour, minute, second))

def Timestamp(year, month, day, hour, minute, second):
    return sybdatetime('%s-%s-%s %d:%d:%d' % (year, month, day,
                                              hour, minute, second))
def DateFromTicks(ticks):
    return apply(Date, time.localtime(ticks)[:3])

def TimeFromTicks(ticks):
    return apply(Time, time.localtime(ticks)[3:6])

def TimestampFromTicks(ticks):
    return apply(Timestamp, time.localtime(ticks)[:6])

def Binary(str):
    return str

DateTimeAsSybase = {}

try:
    import DateTime as mxDateTime
except ImportError:
    try:
        import mx.DateTime as mxDateTime
    except:
        mxDateTime = None
if mxDateTime:
    DateTimeAsMx = {
        CS_DATETIME_TYPE: lambda val: mxDateTime.DateTime(val.year, val.month + 1, val.day,
                                                          val.hour, val.minute,
                                                          val.second + val.msecond / 1000.0),
        CS_DATETIME4_TYPE: lambda val: mxDateTime.DateTime(val.year, val.month + 1, val.day,
                                                           val.hour, val.minute,
                                                           val.second + val.msecond / 1000.0)}
    if _have_cs_date_type:
        DateTimeAsMx.update({
            CS_DATE_TYPE: lambda val: mxDateTime.DateTime(val.year, val.month + 1, val.day) })
    DATETIME += DBAPITypeObject(mxDateTime.DateTimeType)
    def Date(year, month, day):
        return mxDateTime.Date(year, month, day)
    def Time(hour, minute, second):
        return mxDateTime.Time(hour, minute, second)
    def Timestamp(year, month, day, hour, minute, second):
        return mxDateTime.Timestamp(year, month, day, hour, minute, second)
else:
    def mx_import_error(val): raise ImportError, "mx module could not be loaded"
    DateTimeAsMx = { CS_DATETIME_TYPE: mx_import_error,
                     CS_DATETIME4_TYPE: mx_import_error }

try:
    import datetime
    DateTimeAsPython = {
        CS_DATETIME_TYPE: lambda val: datetime.datetime(val.year, val.month + 1, val.day,
                                                        val.hour, val.minute,
                                                        val.second, val.msecond * 1000),
        CS_DATETIME4_TYPE: lambda val: datetime.datetime(val.year, val.month + 1, val.day,
                                                         val.hour, val.minute,
                                                         val.second, val.msecond * 1000) }
    if _have_cs_date_type:
        DateTimeAsPython.update({
            CS_DATE_TYPE: lambda val: datetime.date(val.year, val.month + 1, val.day) })
    DATETIME += DBAPITypeObject(datetime.datetime, datetime.date, datetime.time)
    def Date(year, month, day):
        return datetime.datetime(year, month, day)
    def Time(hour, minute, second):
        return datetime.time(hour, minute, second)
    def Timestamp(year, month, day, hour, minute, second):
        return datetime.datetime(year, month, day, hour, minute, second)
except ImportError:
    def datetime_import_error(val): raise ImportError, "datetime module could not be loaded"
    DateTimeAsPython = { CS_DATETIME_TYPE: datetime_import_error,
                         CS_DATETIME4_TYPE: datetime_import_error }    


_output_hooks = {}

def _fmt_server(msg):
    parts = []
    for label, name in (('Msg', 'msgnumber'),
                        ('Level', 'severity'),
                        ('State', 'state'),
                        ('Procedure', 'proc'),
                        ('Line', 'line')):
        value = getattr(msg, name)
        if value:
            parts.append('%s %s' % (label, value))
    text = '%s\n%s' % (string.join(parts, ', '), msg.text)
    _ctx.debug_msg(text)
    return text


def _fmt_client(msg):
    text = 'Layer: %s, Origin: %s\n' \
           '%s' % (CS_LAYER(msg.msgnumber), CS_ORIGIN(msg.msgnumber),
                   msg.msgstring)
    _ctx.debug_msg(text)
    return text


def _cslib_cb(ctx, msg):
    raise Error(_fmt_client(msg), msg)


def _clientmsg_cb(ctx, conn, msg):
    raise DatabaseError(msg)


def _servermsg_cb(ctx, conn, msg):
    mn = msg.msgnumber
    if mn == 208: ## Object not found
        raise ProgrammingError(msg)
    elif mn == 2601: ## Attempt to insert duplicate key row in object with unique index
        raise IntegrityError(msg)
    elif mn == 2812: ## Procedure not found
        raise StoredProcedureError(msg)
    elif mn in (0, 5701, 5703, 5704) or ((mn >= 6200) and (mn < 6300)):
        # Non-errors:
        #    0      PRINT
        # 5701      Changed db context
        # 5703      Changed language
        # 5704      Changed character set (Sybase)
        # 6200-6299 SHOWPLAN output (Sybase)
        hook = _output_hooks.get(conn)
        if hook:
            hook(conn, msg)
    else:
        raise DatabaseError(msg)


def _column_value(val, dbtype, outputmap):
    if outputmap is not None:
        converter = outputmap.get(dbtype, None)
        if converter is not None:
            val = converter(val)
    return val


def _extract_row(bufs, n, outputmap=None):
    '''Extract a row tuple from buffers.
    '''
    row = [None] * len(bufs)
    col = 0
    for buf in bufs:
        row[col] = _column_value(buf[n], buf.datatype, outputmap)
        col = col + 1
    _ctx.debug_msg("_extract_row %s\n" % row)
    return tuple(row)


# Setup global library context
status, _ctx = cs_ctx_alloc()
if status != CS_SUCCEED:
    raise InternalError('cs_ctx_alloc failed')
set_global_ctx(_ctx)
if _ctx.ct_init() != CS_SUCCEED:
    raise Error('ct_init')
_ctx.cs_config(CS_SET, CS_MESSAGE_CB, _cslib_cb)
_ctx.ct_callback(CS_SET, CS_CLIENTMSG_CB, _clientmsg_cb)
_ctx.ct_callback(CS_SET, CS_SERVERMSG_CB, _servermsg_cb)
if _ctx.ct_config(CS_SET, CS_NETIO, CS_SYNC_IO) != CS_SUCCEED:
    raise Error('ct_config')


class Cursor:

    def __init__(self, owner, inputmap=None, outputmap=None):
        '''Implements DB-API Cursor object
        '''
        self._owner = owner
        self.inputmap = inputmap
        self.outputmap = outputmap
        self.arraysize = 1              # DB-API
        self._ct_cursor = False
        self._fetching = False
        self._reset()
        status, self._cmd = self._owner._conn.ct_cmd_alloc()
        if status != CS_SUCCEED:
            self._raise_error(Error('ct_cmd_alloc'))

    def _reset(self):
        if self._ct_cursor:
            self._close_ct_cursor()
        elif self._fetching:
            self._cancel_cmd()
        self.rowcount = -1              # DB-API
        self.description = None         # DB-API
        self._result_list = []
        self._rownum = -1
        self._fetching = False
        self._params = None

    def _lock(self):
        self._owner._lock()

    def _unlock(self):
        self._owner._unlock()

    def __del__(self):
        if self._owner._is_connected and self._cmd:
            self.close()

    def _cancel_cmd(self):
        _ctx.debug_msg('_cancel_cmd\n')
        if self._fetching:
            status = self._cmd.ct_cancel(CS_CANCEL_CURRENT)
        while 1:
            try:
                status, result = self._cmd.ct_results()
            except DatabaseError:
                continue
            if status == CS_END_RESULTS:
                self._fetching = False
                break
            if result in (CS_ROW_RESULT, CS_PARAM_RESULT, CS_COMPUTE_RESULT):
                status = self._cmd.ct_cancel(CS_CANCEL_CURRENT)
            elif result == CS_STATUS_RESULT:
                _bufs = self._row_bind(1)
                status_result = []
                while self._fetch_rows(_bufs, status_result):
                    pass

    def callproc(self, name, params = ()):
        '''DB-API Cursor.callproc()
        '''
        self._lock()
        try:
            # Discard any previous results
            self._reset()

            # Prepare to retrieve new results.
            status = self._cmd.ct_command(CS_RPC_CMD, name)
            if status != CS_SUCCEED:
                self._raise_error(Error('ct_command'))
            # Send parameters.
            if type(params) is type({}):
                out_params = {}
                for name, value in params.items():
                    out_params[name] = value
                    if isinstance(value, DataBufType):
                        buf = value
                    else:
                        if self.inputmap is not None:
                            for tp in type(value).__mro__:
                                converter = cursor.inputmap.get(tp, None)
                                if converter is not None:
                                    break
                            if converter is not None:
                                value = converter(value)
                        buf = DataBuf(value)
                    buf.name = name
                    status = self._cmd.ct_param(buf)
                    if status != CS_SUCCEED:
                        self._raise_error(Error('ct_param'))
            else:
                out_params = []
                for value in params:
                    if self.inputmap is not None:
                        for tp in type(value).__mro__:
                            converter = cursor.inputmap.get(tp, None)
                            if converter is not None:
                                break
                        if converter is not None:
                            value = converter(value)
                    out_params.append(value)
                    if isinstance(value, DataBufType):
                        buf = value
                    else:
                        buf = DataBuf(value)
                    status = self._cmd.ct_param(buf)
                    if status != CS_SUCCEED:
                        self._raise_error(Error('ct_param'))
            # Start retreiving results.
            self._start()
            return out_params
        finally:
            self._unlock()

    def close(self):
        '''DB-API Cursor.close()
        '''
        if not self._cmd:
            raise ProgrammingError('cursor is already closed')

        _ctx.debug_msg("_close_cursor starts\n")

        self._reset()
        self._cmd.ct_cmd_drop()
        self._cmd = None

    def _close_ct_cursor(self):
        self._ct_cursor = False

        status = self._cmd.ct_cursor(CS_CURSOR_CLOSE)
        if status != CS_SUCCEED:
            self._raise_error(Error('ct_cursor close'))
        status = self._cmd.ct_send()
        if status != CS_SUCCEED:
            self._raise_error(Error('ct_send'))
        while 1:
            status, result = self._cmd.ct_results()
            if status != CS_SUCCEED:
                break

        status = self._cmd.ct_cursor(CS_CURSOR_DEALLOC)
        if status != CS_SUCCEED:
            self._raise_error(Error('ct_cursor dealloc'))
        status = self._cmd.ct_send()
        if status != CS_SUCCEED:
            self._raise_error(Error('ct_send'))
        while 1:
            status, result = self._cmd.ct_results()
            if status != CS_SUCCEED:
                break

    def prepare(self, sql, select = None):
        '''Prepare to retrieve new results.
        '''
        self._lock()
        try:
            if not self._owner._is_connected:
                raise ProgrammingError('Connection is not connected')
            self._reset()
            #if select is True or (select is None and sql.lower().startswith("select")):
            if False:
                self._ct_cursor = True
                _ctx.debug_msg("using ct_cursor, \"%s\"\n" % sql)
                status = self._cmd.ct_cursor(CS_CURSOR_DECLARE, "ctmp%x" % id(self), sql, CS_UNUSED)
                if status != CS_SUCCEED:
                    self._raise_error(Error('ct_cursor declare'))
            else:
                self._ct_cursor = False
                self._cmd.ct_command(CS_LANG_CMD, sql)
        finally:
            self._unlock()

    def execute(self, sql, params = {}, select = None):
        '''DB-API Cursor.execute()
        '''
        self._lock()
        try:
            if sql is not None:
                self.prepare(sql, select)
            if self._params is None:
                self._params = {}
                for name, value in params.items():
                    if self.inputmap is not None:
                        for tp in type(value).__mro__:
                            converter = self.inputmap.get(tp, None)
                            if converter is not None:
                                break
                        if converter is not None:
                            value = converter(value)
    
                    buf = DataBuf(value)
                    buf.name = name
                    self._params[name] = buf
    
                    if self._ct_cursor:
                        # declaring parameters fmt
                        fmt = CS_DATAFMT()
                        fmt.count = buf.count
                        fmt.datatype = buf.datatype
                        fmt.format = CS_FMT_UNUSED
                        fmt.maxlength = buf.maxlength
                        fmt.name = buf.name
                        fmt.precision = buf.precision
                        fmt.scale = buf.scale
                        fmt.status = CS_INPUTVALUE
                        fmt.strip = buf.strip
                        fmt.usertype = buf.usertype
                        status = self._cmd.ct_param(fmt)
                        if status != CS_SUCCEED:
                            self._raise_error(Error('ct_param'))
    
                if self._ct_cursor:
                    ## SSA: CS_CURSOR_ROWS does not seem to be taken into account
                    # nb_rows = 100
                    # self._cmd.ct_cursor(CS_CURSOR_ROWS, nb_rows)
                    # _ctx.debug_msg("using ct_cursor nb_rows %d\n" % nb_rows)
                    # if status != CS_SUCCEED:
                    #     self._raise_error(Error('ct_cursor rows'))
    
                    _ctx.debug_msg("cursor open\n")
                    status = self._cmd.ct_cursor(CS_CURSOR_OPEN)
                    if status != CS_SUCCEED:
                        self._raise_error(Error('ct_cursor open'))
    
                for name in params.keys():
                    status = self._cmd.ct_setparam(self._params[name])
                    if status != CS_SUCCEED:
                        self._raise_error(Error('ct_param'))
            else:
                for name, value in params.items():
                    if self.inputmap is not None:
                        for tp in type(value).__mro__:
                            converter = self.inputmap.get(tp, None)
                            if converter is not None:
                                break
                        if converter is not None:
                            value = converter(value)
                    self._params[name][0] = value
            self._start()
        finally:
            self._unlock()

    def executemany(self, sql, params_seq = []):
        '''DB-API Cursor.executemany()
        '''
        self.prepare(sql, False)
        for params in params_seq:
            self.execute(None, params)
            if self._fetching:
                self._raise_error(ProgrammingError('fetchable results on cursor'))

    def setinputsizes(self, *sizes):
        '''DB-API Cursor.setinputsizes()
        '''
        pass

    def setoutputsize(self, size, column = None):
        '''DB-API Cursor.setoutputsize()
        '''
        pass

    def fetchone(self):
        '''DB-API Cursor.fetchone()
        '''
        self._lock()
        try:
            if self._rownum == -1:
                self._raise_error(Error('No result set'))
            elif self._rownum == 0 and self._fetching:
                self._row_result()
            if self._rownum > 0:
                self._rownum -= 1
                return self._result_list.pop(0)
            return None
        finally:
            self._unlock()

    def fetchmany(self, num = -1):
        '''DB-API Cursor.fetchmany()
        '''
        self._lock()
        try:
            if self._rownum == -1:
                self._raise_error(Error('No result set'))
            if num < 0:
                num = self.arraysize
            while num > self._rownum and self._fetching:
                self._row_result()
            res = self._result_list[0:num]
            del self._result_list[0:num]
            self._rownum -= num
            return res
        finally:
            self._unlock()

    def fetchall(self):
        '''DB-API Cursor.fetchall()
        '''
        self._lock()
        try:
            if self._rownum == -1:
                self._raise_error(Error('No result set'))
            while self._fetching:
                self._row_result()
            res = self._result_list
            self._result_list = []
            self._rownum = 0
            return res
        finally:
            self._unlock()

    def nextset(self):
        '''DB-API Cursor.nextset()
        '''
        self._lock()
        try:
            if not self._fetching:
                return None
            status = self._cmd.ct_cancel(CS_CANCEL_CURRENT)
            self._result_list = []
            self._rownum = -1
            self.rowcount = -1
            self._mainloop()
            if self._result_list:
                return True
            return None
        finally:
            self._unlock()

    def _row_bind(self, count = 1):
        '''Bind buffers for count rows of column data.
        '''
        status, num_cols = self._cmd.ct_res_info(CS_NUMDATA)
        if status != CS_SUCCEED:
            raise Error('ct_res_info')
        bufs = []
        for i in range(num_cols):
            status, fmt = self._cmd.ct_describe(i + 1)
            if status != CS_SUCCEED:
                raise Error('ct_describe')
            fmt.count = count
            if fmt.datatype == CS_VARBINARY_TYPE:
                fmt.datatype = CS_BINARY_TYPE
            if fmt.maxlength > 65536:
                fmt.maxlength = 65536
            status, buf = self._cmd.ct_bind(i + 1, fmt)
            if status != CS_SUCCEED:
                raise Error('ct_bind')
            bufs.append(buf)
        _ctx.debug_msg("_row_bind -> %s\n" % bufs)
        return bufs

    def _fetch_rows(self, bufs, rows):
        '''Fetch rows into bufs.
    
        When bound to buffers for a single row, return a row tuple.
        When bound to multiple row buffers, return a list of row
        tuples.
        '''
        status, rows_read = self._cmd.ct_fetch()
        if status == CS_SUCCEED:
            pass
        elif status == CS_END_DATA:
            # return self._mainloop()
            return 0
        elif status in (CS_ROW_FAIL, CS_FAIL, CS_CANCELED):
            raise Error('ct_fetch')
        if bufs[0].count > 1:
            for i in xrange(rows_read):
                rows.append(_extract_row(bufs, i, self.outputmap))
            _ctx.debug_msg('_fetch_rows -> %s\n' % rows)
            return rows_read
        else:
            rows.append(_extract_row(bufs, 0, self.outputmap))
            _ctx.debug_msg('_fetch_rows -> %s\n' % rows)
            return 1

    def _start(self):
        self._result_list = []
        self._rownum = -1
        self.rowcount = -1
        self.description = None

        status = self._cmd.ct_send()
        if status != CS_SUCCEED:
            self._raise_error(Error('ct_send'))
        self._fetching = True
        return self._mainloop()

    def _bufs_description(self):
        self.description = [(buf.name, buf.datatype, 0, buf.maxlength, buf.precision, buf.scale,
                             buf.status & CS_CANBENULL) for buf in self._bufs]

    def _mainloop(self):
        while 1:
            try:
                status, result = self._cmd.ct_results()
            except Exception, e:
                # When an exception occurs on a ct_cursor, the
                # ct_cursor can get lost by sybase
                self._ct_cursor = False
                self._raise_error(e)
            if status == CS_END_RESULTS:
                self._fetching = False
                return 0
            elif status != CS_SUCCEED:
                self._raise_error(Error('ct_results (status %d, %s)' % (status, str(result))))

            if result in (CS_PARAM_RESULT, CS_COMPUTE_RESULT):
                # A single row
                self._rownum = 0
                self._bufs = self._row_bind(1)
                self._bufs_description()
                self._read_results()
                return 1
            elif result in (CS_ROW_RESULT, CS_CURSOR_RESULT):
                # Zero or more rows of tabular data.
                self._rownum = 0
                self._bufs = self._row_bind(self.arraysize)
                self._bufs_description()
                self._row_result()
                return 1
            elif result == CS_STATUS_RESULT:
                # Stored procedure return status results - A single row containing a single status.
                self._rownum = 0
                self._bufs = self._row_bind(1)
                self._status_result()
                return 0
            elif result == CS_CMD_DONE:
                # End of a result set
                # status, self.rowcount = self._cmd.ct_res_info(CS_ROW_COUNT)
                # if status != CS_SUCCEED:
                #     self._raise_error(Error, 'ct_res_info')
                continue
            elif result == CS_CMD_SUCCEED:
                continue
            else:
                self._raise_error(Error('ct_results (status %d, %s)' % (status, str(result))))

    def _is_idle(self):
        return not self._fetching

    def _raise_error(self, exc):
        _ctx.debug_msg("Cursor._raise_error\n")
        self._reset()
        raise exc

    def _read_results(self):
        logical_result = []
        count = 1
        while self._fetching:
            count = self._fetch_rows(self._bufs, logical_result)
            self._rownum += count
            if not count:
                self._mainloop()
        self._result_list += logical_result

    def _row_result(self):
        logical_result = []
        count = self._fetch_rows(self._bufs, logical_result)
        if not count:
            self._mainloop()
        self._rownum += count
        self._result_list += logical_result

    def _status_result(self):
        status_result = []
        while self._fetch_rows(self._bufs, status_result):
            pass
        self._mainloop()


class Connection:

    def __init__(self, dsn, user, passwd, database = None,
                 strip = 0, auto_commit = 0, delay_connect = 0, locking = 1,
                 datetime = None, bulkcopy = 0, locale = None,
                 inputmap = None, outputmap = None ):
        '''DB-API Sybase.Connect()
        '''
        self._conn = self._cmd = None
        self.dsn = dsn
        self.user = user
        self.passwd = passwd
        self.database = database
        self.auto_commit = auto_commit
        self._do_locking = locking
        self._is_connected = 0
        self.arraysize = 32
        self.inputmap = inputmap
        self.outputmap = outputmap

        # Backward compatibility with datetime kwarg
        if datetime is not None:
            global use_datetime
            import warnings
            warnings.warn("native python datetime is deprecated - use inputmap and outputmap instead", DeprecationWarning)
            if datetime == "auto":
                self.outputmap = DateTimeAsPython
                use_datetime = 2
            elif datetime == "sybase":
                self.outputmap = DateTimeAsSybase
                use_datetime = 0
            elif datetime == "mx":
                self.outputmap = DateTimeAsMx
                use_datetime = 1
            elif datetime == "python":
                self.outputmap = DateTimeAsPython
                use_datetime = 2
            else:
                raise ValueError, "Unknown datetime value: %s" % datetime

        if locking:
            self._connlock = threading.RLock()

        # Do not lock in sybasect - we take care if locking in Python.
        status, conn = _ctx.ct_con_alloc(0)
        if status != CS_SUCCEED:
            raise Error('ct_con_alloc')
        self._conn = conn
        conn.strip = strip
        status = conn.ct_con_props(CS_SET, CS_USERNAME, user)
        if status != CS_SUCCEED:
            self._raise_error(Error('ct_con_props'))
        status = conn.ct_con_props(CS_SET, CS_PASSWORD, passwd)
        if status != CS_SUCCEED:
            self._raise_error(Error('ct_con_props'))
        if bulkcopy:
            status = conn.ct_con_props(CS_SET, CS_BULK_LOGIN, CS_TRUE)
            if status != CS_SUCCEED:
                self._raise_error(Error('ct_con_props'))
        if locale:
            status, loc = _ctx.cs_loc_alloc()
            if status != CS_SUCCEED:
                self._raise_error(Error('cs_loc_alloc'))
            status = loc.cs_locale(CS_SET, CS_SYB_CHARSET, locale)
            if status != CS_SUCCEED:
                self._raise_error(Error('cs_locale'))
            status = conn.ct_con_props(CS_SET, CS_LOC_PROP, loc)
            if status != CS_SUCCEED:
                self._raise_error(Error('ct_con_props'))
        if not delay_connect:
            self.connect()


    def __getattr__(self, name):
        # Expose exception classes via the Connection object so
        # programmers don't have to tie their code to this module with
        # "from Sybase import DatabaseError" all over the place.  See
        # PEP 249, "Optional DB API Extensions".
        names = ('Warning',
                 'Error',
                 'InterfaceError',
                 'DatabaseError',
                 'DataError',
                 'OperationalError',
                 'IntegrityError',
                 'InternalError',
                 'ProgrammingError',
                 'StoredProcedureError',
                 'NotSupportedError',
                )
        if name in names:
            return globals()[name]
        else:
            raise AttributeError(name)

    def _lock(self):
        if self._do_locking:
            _ctx.debug_msg("locking\n")
            self._connlock.acquire()

    def _unlock(self):
        if self._do_locking:
            _ctx.debug_msg("unlocking\n")
            self._connlock.release()

    def _raise_error(self, exc):
        if self._is_connected:
            self._conn.ct_cancel(CS_CANCEL_ALL)
        raise exc

    def connect(self):
        conn = self._conn
        self._lock()
        try:
            status = conn.ct_connect(self.dsn)
            if status != CS_SUCCEED:
                self._raise_error(Error('ct_connect'))
            self._is_connected = 1
            status = conn.ct_options(CS_SET, CS_OPT_CHAINXACTS, not self.auto_commit)
            if status != CS_SUCCEED:
                self._raise_error(Error('ct_options'))
        finally:
            self._unlock()
        if self.database:
            self.execute('use %s' % self.database)
        self._dyn_num = 0

    def get_property(self, prop):
        conn = self._conn
        self._lock()
        try:
            status, value = conn.ct_con_props(CS_GET, prop)
            if status != CS_SUCCEED:
                self._raise_error(Error('ct_con_props'))
        finally:
            self._unlock()
        return value

    def set_property(self, prop, value):
        conn = self._conn
        self._lock()
        try:
            status = conn.ct_con_props(CS_SET, prop, value)
            if status != CS_SUCCEED:
                self._raise_error(Error('ct_con_props'))
        finally:
            self._unlock()

    def set_output_hook(self, hook):
        if hook is None:
            if _output_hooks.has_key(self._conn):
                del _output_hooks[self._conn]
        else:
            _output_hooks[self._conn] = hook

    def get_output_hook(self):
        return _output_hooks.get(self._conn)

    def __del__(self):
        if self._is_connected:
            self.close()

    def close(self):
        '''DBI-API Connection.close()
        '''
        _ctx.debug_msg("Connection.close\n")
        if not self._is_connected:
            raise ProgrammingError('Connection is already closed')
        conn = self._conn
        self._lock()
        try:
            if self._cmd:
                self._cmd.close()
                self._cmd = None

            status = conn.ct_cancel(CS_CANCEL_ALL)
            if status != CS_SUCCEED:
                while 1:
                    status, result = conn.ct_results()
                    if status != CS_SUCCEED:
                        break

            status, result = conn.ct_con_props(CS_GET, CS_CON_STATUS)
            if status != CS_SUCCEED:
                self._raise_error(Error('ct_con_props'))
            if not result & CS_CONSTAT_CONNECTED:
                # Connection is dead
                self._is_connected = 0
                self._raise_error(ProgrammingError('Connection is already closed'))

                status = conn.ct_close(CS_FORCE_CLOSE)
                if status != CS_SUCCEED:
                    self._raise_error(Error('ct_close'))
            else:
                status = conn.ct_close(CS_UNUSED)
                if status != CS_SUCCEED:
                    status = conn.ct_close(CS_FORCE_CLOSE)
                    if status != CS_SUCCEED:
                        self._raise_error(Error('ct_close'))

            conn.ct_con_drop()
            self._conn = conn = None
        finally:
            self._is_connected = 0
            self._unlock()

    def begin(self, name = None):
        '''Not in DB-API, but useful for Sybase
        '''
        if name:
            self.execute('begin transaction %s' % name)
        else:
            self.execute('begin transaction')

    def commit(self, name = None):
        '''DB-API Connection.commit()
        '''
        if not self._is_connected:
            raise ProgrammingError('Connection is not connected')
        if name:
            self.execute('commit transaction %s' % name)
        else:
            self.execute('commit transaction')

    def rollback(self, name = None):
        '''DB-API Connection.rollback()
        '''
        if name:
            self.execute('rollback transaction %s' % name)
        else:
            self.execute('rollback transaction')

    def cursor(self, inputmap = None, outputmap = None):
        '''DB-API Connection.cursor()
        '''
        if inputmap is None and self.inputmap:
            inputmap = copy.copy(self.inputmap)
        if outputmap is None and self.outputmap:
            outputmap = copy.copy(self.outputmap)
        return Cursor(self, inputmap, outputmap)
 
    def bulkcopy(self, tablename, *args, **kw):
        # Fake an alternate way to specify direction=CS_BLK_OUT
        if kw.get('out', 0):
            del kw['out']
            kw['direction'] = CS_BLK_OUT
        return Bulkcopy(self, tablename, *args, **kw)
    
    def execute(self, sql):
        '''Backwards compatibility
        '''
        self._lock()
        try:
            cursor = self.cursor()
            cursor.execute(sql)
            cursor.close()
        finally:
            self._unlock()


class Bulkcopy(object):

    def __init__(self, conn, tablename, direction = CS_BLK_IN, arraysize = 20):
        '''Manage a BCP session for the named table'''

        if not conn.auto_commit:
            raise ProgrammingError('bulkcopy requires connection in auto_commit mode')
        if direction not in (CS_BLK_IN, CS_BLK_OUT):
            raise ProgrammingError("Bulkcopy direction must be CS_BLK_IN or CS_BLK_OUT")
        
        self._direction = direction
        self._arraysize = arraysize     # no of rows to transfer at once
        
        self._totalcount = 0            # Total number of rows transferred in/out so far
        # the next two for _flush() / _row()
        self._batchcount = 0            # Rows send in the current batch but not yet reported to user via self.batch()
        self._nextrow = 0               # Next row in the DataBuf to use
        
        self._alldone = 0

        conn._lock()
        try:
            #conn._conn.debug = 1
            status, blk = conn._conn.blk_alloc()
            if status != CS_SUCCEED:
                conn._raise_error(Error('blk_alloc'))
            if blk.blk_init(direction, tablename) != CS_SUCCEED:
                conn._raise_error(Error('blk_init'))
            #blk.debug = 1
        finally:
            conn._unlock()

        self._blk = blk
        
        # Now allocate buffers
        bufs = []
        while 1:
            try:
                status, fmt = blk.blk_describe(len(bufs) + 1)
                # This never happens, raises DatabaseError instead
                if status != CS_SUCCEED:
                    break
            except DatabaseError, e:
                break
            fmt.count = arraysize
            bufs.append(DataBuf(fmt))

        self.bufs = bufs

        # Now bind the buffers
        for i in range(len(bufs)):
            buf = bufs[i]
            if direction == CS_BLK_OUT:
                buf.format = 0
            else:
                buf.format = CS_BLK_ARRAY_MAXLEN
            if blk.blk_bind(i + 1, buf) != CS_SUCCEED:
                conn._raise_error(Error('blk_bind'))

    def __del__(self):
        '''Make sure any incoming but unflushed data is sent!'''
        try:
            if not self._alldone:
                self.done()
        except:
            pass
            
    # Read-only property, as size of DataBufs is set in __init__
    arraysize = property(lambda x: x._arraysize)
    totalcount = property(lambda x: x._totalcount)
    
    def rowxfer(self, args = None):
        if self._direction == CS_BLK_OUT:
            if args is not None:
                raise ProgramError("Attempt to rowxfer() data in to a bcp out session")
            return self._row()
        
        if args is None:
            raise ProgramError("rowxfer() for bcp-IN needs a sequence arg")
            
        if len(args) != len(self.bufs):
            raise Error("BCP has %d columns, data has %d columns" % (len(self.bufs), len(args)))

        for i in range(len(args)):
            self.bufs[i][self._nextrow] = args[i]
        self._nextrow += 1

        if self._nextrow == self._arraysize:
            self._flush()

    def _flush(self):
        '''Flush any partially-filled DataBufs'''
        if self._nextrow > 0:
            status, rows  = self._blk.blk_rowxfer_mult(self._nextrow)
            if status != CS_SUCCEED:
                self.conn._raise_error(Error('blk_rowxfer_mult in'))
            self._nextrow = 0
            self._totalcount += rows
            
    def batch(self):
        '''Flush a batch full to the server.  Return the number of rows in this batch'''
        self._flush()
        status, rows = self._blk.blk_done(CS_BLK_BATCH)
        if status != CS_SUCCEED:
            self.conn._raise_error(Error('blk_done batch in'))
        # rows should be 0 here due to _flush()
        rows += self._batchcount
        self._batchcount = 0
        return rows
            
    def done(self):
        self._flush()
        status, rows = self._blk.blk_done(CS_BLK_ALL)
        if status != CS_SUCCEED:
            self.conn._raise_error(Error('blk_done in'))
        self._alldone = 1
        return rows        

    def __iter__(self):
        '''An iterator for all the BCPd rows fetched from the database'''
        if self._direction == CS_BLK_IN:
            raise ProgramError("iter() is for bcp-OUT... use rowxfer() instead")
        while 1:
            r = self._row()
            if r is None:
                raise StopIteration
            yield r
    rows = __iter__

    def _row(self):
        if self._nextrow == self._batchcount:
            status, num = self._blk.blk_rowxfer_mult()
            if status == CS_END_DATA:
                status, rows = self._blk.blk_done(CS_BLK_ALL)
                if status != CS_SUCCEED:
                    self.conn._raise_error(Error('blk_done out'))
                self._alldone = 1
                return None
            if status != CS_SUCCEED:
                self.conn._raise_error(Error('blk_rowxfer_mult out'))
            self._nextrow = 0
            self._batchcount = num
            assert num > 0
        self._totalcount += 1
        rownum = self._nextrow
        self._nextrow += 1
        return _extract_row(self.bufs, rownum)


def connect(dsn, user, passwd, database = None,
            strip = 0, auto_commit = 0, delay_connect = 0, locking = 1, datetime = None,
            bulkcopy = 0, locale = None, inputmap = None, outputmap = None):
    return Connection(dsn, user, passwd, database,
                      strip, auto_commit, delay_connect, locking,
                      datetime, bulkcopy, locale, inputmap, outputmap)
