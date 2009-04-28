/******************************************************************

 Copyright 2001 by Object Craft P/L, Melbourne, Australia.

 LICENCE - see LICENCE file distributed with this software for details.

******************************************************************/

#include "sybasect.h"
#ifdef HAVE_DATETIME
#include "datetime.h"
#endif

#ifdef HAVE_DECIMAL
PyObject *DecimalClass;
#endif

#ifdef FIND_LEAKS
typedef struct LeakReg {
    PyObject *obj;
    struct LeakReg *next;
} LeakReg;

static LeakReg *all_objs;
static int num_objs;

void leak_reg(PyObject *obj)
{
    LeakReg *reg = malloc(sizeof(*reg));
    reg->obj = obj;
    reg->next = all_objs;
    all_objs = reg;
    num_objs++;
}

void leak_unreg(PyObject *obj)
{
    LeakReg *reg, *prev;

    for (reg = all_objs, prev = NULL; reg; prev = reg, reg = reg->next)
	if (reg->obj == obj) {
	    if (prev == NULL)
		all_objs = reg->next;
	    else
		prev->next = reg->next;
	    free(reg);
	    num_objs--;
	    return;
	}
    debug_msg("%s not registered!\n", obj->ob_type->tp_name);
}

static PyObject *report_leaks(PyObject *module, PyObject *args)
{
    LeakReg *reg;

    for (reg = all_objs; reg; reg = reg->next)
	debug_msg("%s\n", reg->obj->ob_type->tp_name);
    Py_INCREF(Py_None);
    return Py_None;
}
#endif

int first_tuple_int(PyObject *args, int *int_arg)
{
    PyObject *obj;

    if (!PyTuple_Check(args)) {
	PyErr_SetString(PyExc_SystemError, "argument is not a tuple");
	return 0;
    }
    obj = PyTuple_GetItem(args, 0);
    if (obj == NULL)
	return 0;
    *int_arg = PyInt_AsLong(obj);
    return !PyErr_Occurred();
}

static char *module = "sybasect";

static PyObject *debug_file = NULL;

void debug_msg(char *fmt, ...)
{
    char buff[10240];
    va_list ap;
    PyObject *res;

    if (debug_file == Py_None)
	return;

    va_start(ap, fmt);
#ifdef _WIN32
    _vsnprintf(buff, sizeof(buff), fmt, ap);
#else
    vsnprintf(buff, sizeof(buff), fmt, ap);
#endif
    va_end(ap);

    res = PyObject_CallMethod(debug_file, "write", "s", buff);
    Py_XDECREF(res);
    /* PyErr_Clear(); */
    res = PyObject_CallMethod(debug_file, "flush", "");
    Py_XDECREF(res);
    /* PyErr_Clear(); */
}

/* PyDate_Check must be called in the same source file as
   PyDateTime_IMPORT so we create this alias */
int pydate_check(PyObject *ob)
{
#ifdef HAVE_DATETIME
    return PyDate_Check(ob);
#else
    return 0;
#endif
}

/* PyDateTime_Check must be called in the same source file as
   PyDateTime_IMPORT so we create this alias */
int pydatetime_check(PyObject *ob)
{
#ifdef HAVE_DATETIME
    return PyDateTime_Check(ob);
#else
    return 0;
#endif
}

int pydecimal_check(PyObject *ob)
{
#ifdef HAVE_DECIMAL
    return PyObject_IsInstance(ob, DecimalClass);
#else
    return 0;
#endif
}

static char sybasect_set_debug__doc__[] = 
"set_debug(file) -> old_file";

static PyObject *sybasect_set_debug(PyObject *module, PyObject *args)
{
    PyObject *obj, *res;

    if (!PyArg_ParseTuple(args, "O", &obj))
	return NULL;

    if (obj != Py_None) {
	res = PyObject_CallMethod(obj, "write", "s", "");
	Py_XDECREF(res);
	if (res == NULL)
	    return NULL;
	res = PyObject_CallMethod(obj, "flush", "");
	Py_XDECREF(res);
	if (res == NULL)
	    return NULL;
    }

    res = debug_file;
    debug_file = obj;
    Py_INCREF(debug_file);
    return res;
}

static char sybasect_cs_ctx_alloc__doc__[] =
"cs_ctx_alloc([version]) -> ctx\n"
"\n"
"Allocate a new Sybase library context object.";

static PyObject *sybasect_cs_ctx_alloc(PyObject *module, PyObject *args)
{
    int version = CS_VERSION_100;

    if (!PyArg_ParseTuple(args, "|i", &version))
	return NULL;
    return ctx_alloc(version);
}

static char sybasect_set_global_ctx__doc__[] =
"set_global_ctx(ctx)\n"
"\n"
"Set the internal Sybase library context object.";

static PyObject *sybasect_set_global_ctx(PyObject *module, PyObject *args)
{
    CS_CONTEXTObj *ctx;

    if (!PyArg_ParseTuple(args, "O!", &CS_CONTEXTType, &ctx))
	return NULL;

    return set_global_ctx(ctx);
}

static char sybasect_DataBuf__doc__[] =
"DataBuf(obj) -> buffer\n"
"\n"
"Allocate a buffer to store data described by datafmt or object type.";

static PyObject *sybasect_DataBuf(PyObject *module, PyObject *args)
{
    PyObject *obj;

    if (!PyArg_ParseTuple(args, "O", &obj))
	return NULL;

    return databuf_alloc(obj);
}

static char sybasect_CS_LAYER__doc__[] =
"CS_LAYER(int) -> int\n"
"\n"
"Isolate layer from message number.";

static PyObject *sybasect_CS_LAYER(PyObject *module, PyObject *args)
{
    int num;

    if (!PyArg_ParseTuple(args, "i", &num))
	return NULL;

    return PyInt_FromLong(CS_LAYER(num));
}

static char sybasect_CS_ORIGIN__doc__[] =
"CS_ORIGIN(int) -> int\n"
"\n"
"Isolate origin from message number.";

static PyObject *sybasect_CS_ORIGIN(PyObject *module, PyObject *args)
{
    int num;

    if (!PyArg_ParseTuple(args, "i", &num))
	return NULL;

    return PyInt_FromLong(CS_ORIGIN(num));
}

static char sybasect_CS_SEVERITY__doc__[] =
"CS_SEVERITY(int) -> int\n"
"\n"
"Isolate severity from message number.";

static PyObject *sybasect_CS_SEVERITY(PyObject *module, PyObject *args)
{
    int num;

    if (!PyArg_ParseTuple(args, "i", &num))
	return NULL;

    return PyInt_FromLong(CS_SEVERITY(num));
}

static char sybasect_CS_NUMBER__doc__[] =
"CS_NUMBER(int) -> int\n"
"\n"
"Isolate number from message number.";

static PyObject *sybasect_CS_NUMBER(PyObject *module, PyObject *args)
{
    int num;

    if (!PyArg_ParseTuple(args, "i", &num))
	return NULL;

    return PyInt_FromLong(CS_NUMBER(num));
}

static char sybasect_sizeof_type__doc__[] =
"sizeof_type(int) -> int\n"
"\n"
"Return the size of a Sybase data type.";

static PyObject *sybasect_sizeof_type(PyObject *module, PyObject *args)
{
    int num;
    int size;

    if (!PyArg_ParseTuple(args, "i", &num))
	return NULL;

    switch (num) {
    case CS_CHAR_TYPE:
	size = sizeof(CS_CHAR);
	break;
    case CS_BINARY_TYPE:
	size = sizeof(CS_BINARY);
	break;
    case CS_LONGCHAR_TYPE:
	size = sizeof(CS_LONGCHAR);
	break;
    case CS_LONGBINARY_TYPE:
	size = sizeof(CS_LONGBINARY);
	break;
    case CS_TEXT_TYPE:
	size = sizeof(CS_TEXT);
	break;
    case CS_IMAGE_TYPE:
	size = sizeof(CS_IMAGE);
	break;
    case CS_TINYINT_TYPE:
	size = sizeof(CS_TINYINT);
	break;
    case CS_SMALLINT_TYPE:
	size = sizeof(CS_SMALLINT);
	break;
    case CS_INT_TYPE:
	size = sizeof(CS_INT);
	break;
    case CS_REAL_TYPE:
	size = sizeof(CS_REAL);
	break;
    case CS_FLOAT_TYPE:
	size = sizeof(CS_FLOAT);
	break;
    case CS_BIT_TYPE:
	size = sizeof(CS_BIT);
	break;
    case CS_DATETIME_TYPE:
	size = sizeof(CS_DATETIME);
	break;
    case CS_DATETIME4_TYPE:
	size = sizeof(CS_DATETIME4);
	break;
#ifdef CS_DATE_TYPE
    case CS_DATE_TYPE:
	size = sizeof(CS_DATE);
	break;
#endif
    case CS_MONEY_TYPE:
	size = sizeof(CS_MONEY);
	break;
    case CS_MONEY4_TYPE:
	size = sizeof(CS_MONEY4);
	break;
    case CS_NUMERIC_TYPE:
	size = sizeof(CS_NUMERIC);
	break;
    case CS_DECIMAL_TYPE:
	size = sizeof(CS_DECIMAL);
	break;
#ifndef HAVE_FREETDS
    case CS_VARCHAR_TYPE:
	size = sizeof(CS_VARCHAR);
	break;
    case CS_VARBINARY_TYPE:
	size = sizeof(CS_VARBINARY);
	break;
#endif
    case CS_LONG_TYPE:
	size = sizeof(CS_LONG);
	break;
    case CS_USHORT_TYPE:
	size = sizeof(CS_USHORT);
	break;
#ifdef CS_CLIENTMSG_TYPE
    case CS_CLIENTMSG_TYPE:
	size = sizeof(CS_CLIENTMSG);
	break;
#endif
#ifdef CS_SERVERMSG_TYPE
    case CS_SERVERMSG_TYPE:
	size = sizeof(CS_SERVERMSG);
	break;
#endif
    default:
	PyErr_SetString(PyExc_TypeError, "unknown type");
	return NULL;
    }

    return PyInt_FromLong(size);
}

/* List of methods defined in the module */

static struct PyMethodDef sybasect_methods[] = {
#ifdef FIND_LEAKS
    { "leaks", (PyCFunction)report_leaks, METH_VARARGS, "" },
#endif
    { "cs_ctx_alloc", (PyCFunction)sybasect_cs_ctx_alloc, METH_VARARGS, sybasect_cs_ctx_alloc__doc__ },
    { "set_global_ctx", (PyCFunction)sybasect_set_global_ctx, METH_VARARGS, sybasect_set_global_ctx__doc__ },
    { "DataBuf", (PyCFunction)sybasect_DataBuf, METH_VARARGS, sybasect_DataBuf__doc__ },
    { "numeric", (PyCFunction)NumericType_new, METH_VARARGS, NumericType_new__doc__ },
    { "money", (PyCFunction)MoneyType_new, METH_VARARGS, MoneyType_new__doc__ },
    { "datetime", (PyCFunction)DateTimeType_new, METH_VARARGS, DateTimeType_new__doc__ },
#ifdef CS_DATE_TYPE
    { "date", (PyCFunction)DateType_new, METH_VARARGS, DateType_new__doc__ },
#endif
    { "pickle_datetime", (PyCFunction)pickle_datetime, METH_VARARGS, pickle_datetime__doc__ },
#ifdef CS_DATE_TYPE
    { "pickle_date", (PyCFunction)pickle_date, METH_VARARGS, pickle_date__doc__ },
#endif
    { "pickle_money", (PyCFunction)pickle_money, METH_VARARGS, pickle_money__doc__ },
    { "pickle_numeric", (PyCFunction)pickle_numeric, METH_VARARGS, pickle_numeric__doc__ },
    { "sizeof_type", (PyCFunction)sybasect_sizeof_type, METH_VARARGS, sybasect_sizeof_type__doc__ },
    { "CS_DATAFMT", (PyCFunction)datafmt_new, METH_VARARGS, datafmt_new__doc__ },
    { "CS_IODESC", (PyCFunction)iodesc_new, METH_VARARGS, iodesc_new__doc__ },
    { "CS_LAYER", (PyCFunction)sybasect_CS_LAYER, METH_VARARGS, sybasect_CS_LAYER__doc__ },
    { "CS_ORIGIN", (PyCFunction)sybasect_CS_ORIGIN, METH_VARARGS, sybasect_CS_ORIGIN__doc__ },
    { "CS_SEVERITY", (PyCFunction)sybasect_CS_SEVERITY, METH_VARARGS, sybasect_CS_SEVERITY__doc__ },
    { "CS_NUMBER", (PyCFunction)sybasect_CS_NUMBER, METH_VARARGS, sybasect_CS_NUMBER__doc__ },
    { "set_debug", (PyCFunction)sybasect_set_debug, METH_VARARGS, sybasect_set_debug__doc__ },
    { NULL }			/* sentinel */
};

/* Initialisation function for the module (*must* be called
   initsybasect) */

static char sybasect_module_documentation[] = 
"Thin wrapper on top of the Sybase CT library - intended to be used\n"
"by the Sybase.py module.";

#define SYVAL(t, v) { t, #v, v }

typedef struct {
    int type;
    char *name;
    int value;
} value_desc;

static value_desc sybase_args[] = {
#ifdef CS_VERSION_100
    SYVAL(VAL_CSVER, CS_VERSION_100),
#endif
#ifdef CS_VERSION_110
    SYVAL(VAL_CSVER, CS_VERSION_110),
#endif

#ifdef CS_CACHE
    SYVAL(VAL_ACTION, CS_CACHE),
#endif
#ifdef CS_CLEAR
    SYVAL(VAL_ACTION, CS_CLEAR),
#endif
#ifdef CS_GET
    SYVAL(VAL_ACTION, CS_GET),
#endif
#ifdef CS_INIT
    SYVAL(VAL_ACTION, CS_INIT),
#endif
#ifdef CS_MSGLIMIT
    SYVAL(VAL_ACTION, CS_MSGLIMIT),
#endif
#ifdef CS_SEND
    SYVAL(VAL_ACTION, CS_SEND),
#endif
#ifdef CS_SET
    SYVAL(VAL_ACTION, CS_SET),
#endif
#ifdef CS_STATUS
    SYVAL(VAL_ACTION, CS_STATUS),
#endif
#ifdef CS_SUPPORTED
    SYVAL(VAL_ACTION, CS_SUPPORTED),
#endif

#ifdef CS_CANCEL_ALL
    SYVAL(VAL_CANCEL, CS_CANCEL_ALL),
#endif
#ifdef CS_CANCEL_ATTN
    SYVAL(VAL_CANCEL, CS_CANCEL_ATTN),
#endif
#ifdef CS_CANCEL_CURRENT
    SYVAL(VAL_CANCEL, CS_CANCEL_CURRENT),
#endif

#ifdef CS_CMD_DONE
    SYVAL(VAL_RESULT, CS_CMD_DONE),
#endif
#ifdef CS_CMD_FAIL
    SYVAL(VAL_RESULT, CS_CMD_FAIL),
#endif
#ifdef CS_CMD_SUCCEED
    SYVAL(VAL_RESULT, CS_CMD_SUCCEED),
#endif
#ifdef CS_COMPUTEFMT_RESULT
    SYVAL(VAL_RESULT, CS_COMPUTEFMT_RESULT),
#endif
#ifdef CS_COMPUTE_RESULT
    SYVAL(VAL_RESULT, CS_COMPUTE_RESULT),
#endif
#ifdef CS_CURSOR_RESULT
    SYVAL(VAL_RESULT, CS_CURSOR_RESULT),
#endif
#ifdef CS_DESCRIBE_RESULT
    SYVAL(VAL_RESULT, CS_DESCRIBE_RESULT),
#endif
#ifdef CS_MSG_RESULT
    SYVAL(VAL_RESULT, CS_MSG_RESULT),
#endif
#ifdef CS_PARAM_RESULT
    SYVAL(VAL_RESULT, CS_PARAM_RESULT),
#endif
#ifdef CS_ROWFMT_RESULT
    SYVAL(VAL_RESULT, CS_ROWFMT_RESULT),
#endif
#ifdef CS_ROW_RESULT
    SYVAL(VAL_RESULT, CS_ROW_RESULT),
#endif
#ifdef CS_STATUS_RESULT
    SYVAL(VAL_RESULT, CS_STATUS_RESULT),
#endif

#ifdef CS_ROW_COUNT
    SYVAL(VAL_RESINFO, CS_ROW_COUNT),
#endif
#ifdef CS_CMD_NUMBER
    SYVAL(VAL_RESINFO, CS_CMD_NUMBER),
#endif
#ifdef CS_NUM_COMPUTES
    SYVAL(VAL_RESINFO, CS_NUM_COMPUTES),
#endif
#ifdef CS_NUMDATA
    SYVAL(VAL_RESINFO, CS_NUMDATA),
#endif
#ifdef CS_ORDERBY_COLS
    SYVAL(VAL_RESINFO, CS_ORDERBY_COLS),
#endif
#ifdef CS_NUMORDERCOLS
    SYVAL(VAL_RESINFO, CS_NUMORDERCOLS),
#endif
#ifdef CS_MSGTYPE
    SYVAL(VAL_RESINFO, CS_MSGTYPE),
#endif
#ifdef CS_BROWSE_INFO
    SYVAL(VAL_RESINFO, CS_BROWSE_INFO),
#endif
#ifdef CS_TRANS_STATE
    SYVAL(VAL_RESINFO, CS_TRANS_STATE),
#endif

#ifdef CS_LANG_CMD
    SYVAL(VAL_CMD, CS_LANG_CMD),
#endif
#ifdef CS_RPC_CMD
    SYVAL(VAL_CMD, CS_RPC_CMD),
#endif
#ifdef CS_MSG_CMD
    SYVAL(VAL_CMD, CS_MSG_CMD),
#endif
#ifdef CS_SEND_DATA_CMD
    SYVAL(VAL_CMD, CS_SEND_DATA_CMD),
#endif
#ifdef CS_PACKAGE_CMD
    SYVAL(VAL_CMD, CS_PACKAGE_CMD),
#endif
#ifdef CS_SEND_BULK_CMD
    SYVAL(VAL_CMD, CS_SEND_BULK_CMD),
#endif

#ifdef CS_CURSOR_DECLARE
    SYVAL(VAL_CURSOR, CS_CURSOR_DECLARE),
#endif
#ifdef CS_CURSOR_OPEN
    SYVAL(VAL_CURSOR, CS_CURSOR_OPEN),
#endif
#ifdef CS_CURSOR_ROWS
    SYVAL(VAL_CURSOR, CS_CURSOR_ROWS),
#endif
#ifdef CS_CURSOR_UPDATE
    SYVAL(VAL_CURSOR, CS_CURSOR_UPDATE),
#endif
#ifdef CS_CURSOR_DELETE
    SYVAL(VAL_CURSOR, CS_CURSOR_DELETE),
#endif
#ifdef CS_CURSOR_CLOSE
    SYVAL(VAL_CURSOR, CS_CURSOR_CLOSE),
#endif
#ifdef CS_CURSOR_OPTION
    SYVAL(VAL_CURSOR, CS_CURSOR_OPTION),
#endif
#ifdef CS_CURSOR_DEALLOC
    SYVAL(VAL_CURSOR, CS_CURSOR_DEALLOC),
#endif

#ifdef CS_FOR_UPDATE
    SYVAL(VAL_CURSOROPT, CS_FOR_UPDATE),
#endif
#ifdef CS_READ_ONLY
    SYVAL(VAL_CURSOROPT, CS_READ_ONLY),
#endif
#ifdef CS_DYNAMIC
    SYVAL(VAL_CURSOROPT, CS_DYNAMIC),
#endif
#ifdef CS_RESTORE_OPEN
    SYVAL(VAL_CURSOROPT, CS_RESTORE_OPEN),
#endif
#ifdef CS_MORE
    SYVAL(VAL_CURSOROPT, CS_MORE),
#endif
#ifdef CS_END
    SYVAL(VAL_CURSOROPT, CS_END),
#endif

#ifdef CS_BLK_ALL
    SYVAL(VAL_BULK, CS_BLK_ALL),
#endif
#ifdef CS_BLK_BATCH
    SYVAL(VAL_BULK, CS_BLK_BATCH),
#endif
#ifdef CS_BLK_CANCEL
    SYVAL(VAL_BULK, CS_BLK_CANCEL),
#endif
#ifdef BLK_VERSION_100
    SYVAL(VAL_BULK, BLK_VERSION_100),
#endif
#ifdef BLK_VERSION_110
    SYVAL(VAL_BULK, BLK_VERSION_110),
#endif
#ifdef CS_BLK_ARRAY_MAXLEN
    SYVAL(VAL_BULK, CS_BLK_ARRAY_MAXLEN),
#endif

#ifdef CS_BLK_IN
    SYVAL(VAL_BULKDIR, CS_BLK_IN),
#endif
#ifdef CS_BLK_OUT
    SYVAL(VAL_BULKDIR, CS_BLK_OUT),
#endif

#ifdef BLK_IDENTITY
    SYVAL(VAL_BULKPROPS, BLK_IDENTITY),
#endif
#ifdef BLK_SENSITIVITY_LBL
    SYVAL(VAL_BULKPROPS, BLK_SENSITIVITY_LBL),
#endif
#ifdef BLK_NOAPI_CHK
    SYVAL(VAL_BULKPROPS, BLK_NOAPI_CHK),
#endif
#ifdef BLK_SLICENUM
    SYVAL(VAL_BULKPROPS, BLK_SLICENUM),
#endif
#ifdef BLK_IDSTARTNUM
    SYVAL(VAL_BULKPROPS, BLK_IDSTARTNUM),
#endif
#ifdef ARRAY_INSERT
    SYVAL(VAL_BULKPROPS, ARRAY_INSERT),
#endif

#ifdef CS_PREPARE
    SYVAL(VAL_DYNAMIC, CS_PREPARE),
#endif
#ifdef CS_EXECUTE
    SYVAL(VAL_DYNAMIC, CS_EXECUTE),
#endif
#ifdef CS_EXEC_IMMEDIATE
    SYVAL(VAL_DYNAMIC, CS_EXEC_IMMEDIATE),
#endif
#ifdef CS_DESCRIBE_INPUT
    SYVAL(VAL_DYNAMIC, CS_DESCRIBE_INPUT),
#endif
#ifdef CS_DESCRIBE_OUTPUT
    SYVAL(VAL_DYNAMIC, CS_DESCRIBE_OUTPUT),
#endif
#ifdef CS_DYN_CURSOR_DECLARE
    SYVAL(VAL_DYNAMIC, CS_DYN_CURSOR_DECLARE),
#endif

#ifdef CS_DEALLOC
    SYVAL(VAL_DYNAMIC, CS_DEALLOC),
#endif

#ifdef CS_USERNAME
    SYVAL(VAL_PROPS, CS_USERNAME),
#endif
#ifdef CS_PASSWORD
    SYVAL(VAL_PROPS, CS_PASSWORD),
#endif
#ifdef CS_APPNAME
    SYVAL(VAL_PROPS, CS_APPNAME),
#endif
#ifdef CS_HOSTNAME
    SYVAL(VAL_PROPS, CS_HOSTNAME),
#endif
#ifdef CS_LOGIN_STATUS
    SYVAL(VAL_PROPS, CS_LOGIN_STATUS),
#endif
#ifdef CS_TDS_VERSION
    SYVAL(VAL_PROPS, CS_TDS_VERSION),
#endif
#ifdef CS_CHARSETCNV
    SYVAL(VAL_PROPS, CS_CHARSETCNV),
#endif
#ifdef CS_PACKETSIZE
    SYVAL(VAL_PROPS, CS_PACKETSIZE),
#endif
#ifdef CS_NETIO
    SYVAL(VAL_PROPS, CS_NETIO),
#endif
#ifdef CS_TEXTLIMIT
    SYVAL(VAL_PROPS, CS_TEXTLIMIT),
#endif
#ifdef CS_HIDDEN_KEYS
    SYVAL(VAL_PROPS, CS_HIDDEN_KEYS),
#endif
#ifdef CS_VERSION
    SYVAL(VAL_PROPS, CS_VERSION),
#endif
#ifdef CS_IFILE
    SYVAL(VAL_PROPS, CS_IFILE),
#endif
#ifdef CS_LOGIN_TIMEOUT
    SYVAL(VAL_PROPS, CS_LOGIN_TIMEOUT),
#endif
#ifdef CS_TIMEOUT
    SYVAL(VAL_PROPS, CS_TIMEOUT),
#endif
#ifdef CS_MAX_CONNECT
    SYVAL(VAL_PROPS, CS_MAX_CONNECT),
#endif
#ifdef CS_EXPOSE_FMTS
    SYVAL(VAL_PROPS, CS_EXPOSE_FMTS),
#endif
#ifdef CS_EXTRA_INF
    SYVAL(VAL_PROPS, CS_EXTRA_INF),
#endif
#ifdef CS_EXTRA_INF
    SYVAL(VAL_PROPS, CS_EXTRA_INF),
#endif
#ifdef CS_TRANSACTION_NAME
    SYVAL(VAL_PROPS, CS_TRANSACTION_NAME),
#endif
#ifdef CS_ANSI_BINDS
    SYVAL(VAL_PROPS, CS_ANSI_BINDS),
#endif
#ifdef CS_BULK_LOGIN
    SYVAL(VAL_PROPS, CS_BULK_LOGIN),
#endif
#ifdef CS_LOC_PROP
    SYVAL(VAL_PROPS, CS_LOC_PROP),
#endif
#ifdef CS_MESSAGE_CB
    SYVAL(VAL_PROPS, CS_MESSAGE_CB),
#endif
#ifdef CS_EED_CMD
    SYVAL(VAL_PROPS, CS_EED_CMD),
#endif
#ifdef CS_DIAG_TIMEOUT
    SYVAL(VAL_PROPS, CS_DIAG_TIMEOUT),
#endif
#ifdef CS_DISABLE_POLL
    SYVAL(VAL_PROPS, CS_DISABLE_POLL),
#endif
#ifdef CS_SEC_ENCRYPTION
    SYVAL(VAL_PROPS, CS_SEC_ENCRYPTION),
#endif
#ifdef CS_SEC_CHALLENGE
    SYVAL(VAL_PROPS, CS_SEC_CHALLENGE),
#endif
#ifdef CS_SEC_NEGOTIATE
    SYVAL(VAL_PROPS, CS_SEC_NEGOTIATE),
#endif
#ifdef CS_ENDPOINT
    SYVAL(VAL_PROPS, CS_ENDPOINT),
#endif
#ifdef CS_NO_TRUNCATE
    SYVAL(VAL_PROPS, CS_NO_TRUNCATE),
#endif
#ifdef CS_CON_STATUS
    SYVAL(VAL_PROPS, CS_CON_STATUS),
#endif
#ifdef CS_VER_STRING
    SYVAL(VAL_PROPS, CS_VER_STRING),
#endif
#ifdef CS_ASYNC_NOTIFS
    SYVAL(VAL_PROPS, CS_ASYNC_NOTIFS),
#endif
#ifdef CS_SERVERNAME
    SYVAL(VAL_PROPS, CS_SERVERNAME),
#endif
#ifdef CS_SEC_APPDEFINED
    SYVAL(VAL_PROPS, CS_SEC_APPDEFINED),
#endif
#ifdef CS_NOCHARSETCNV_REQD
    SYVAL(VAL_PROPS, CS_NOCHARSETCNV_REQD),
#endif
#ifdef CS_EXTERNAL_CONFIG
    SYVAL(VAL_PROPS, CS_EXTERNAL_CONFIG),
#endif
#ifdef CS_CONFIG_FILE
    SYVAL(VAL_PROPS, CS_CONFIG_FILE),
#endif
#ifdef CS_CONFIG_BY_SERVERNAME
    SYVAL(VAL_PROPS, CS_CONFIG_BY_SERVERNAME),
#endif

#ifdef CS_DS_CHAIN
    SYVAL(VAL_DIRSERV, CS_DS_CHAIN),
#endif
#ifdef CS_DS_EXPANDALIAS
    SYVAL(VAL_DIRSERV, CS_DS_EXPANDALIAS),
#endif
#ifdef CS_DS_COPY
    SYVAL(VAL_DIRSERV, CS_DS_COPY),
#endif
#ifdef CS_DS_SIZELIMIT
    SYVAL(VAL_DIRSERV, CS_DS_SIZELIMIT),
#endif
#ifdef CS_DS_TIMELIMIT
    SYVAL(VAL_DIRSERV, CS_DS_TIMELIMIT),
#endif
#ifdef CS_DS_PRINCIPAL
    SYVAL(VAL_DIRSERV, CS_DS_PRINCIPAL),
#endif
#ifdef CS_DS_SEARCH
    SYVAL(VAL_DIRSERV, CS_DS_SEARCH),
#endif
#ifdef CS_DS_DITBASE
    SYVAL(VAL_DIRSERV, CS_DS_DITBASE),
#endif
#ifdef CS_DS_FAILOVER
    SYVAL(VAL_DIRSERV, CS_DS_FAILOVER),
#endif
#ifdef CS_DS_PROVIDER
    SYVAL(VAL_DIRSERV, CS_DS_PROVIDER),
#endif
#ifdef CS_RETRY_COUNT
    SYVAL(VAL_DIRSERV, CS_RETRY_COUNT),
#endif
#ifdef CS_LOOP_DELAY
    SYVAL(VAL_DIRSERV, CS_LOOP_DELAY),
#endif
#ifdef CS_DS_PASSWORD
    SYVAL(VAL_DIRSERV, CS_DS_PASSWORD),
#endif

#ifdef CS_SEC_NETWORKAUTH
    SYVAL(VAL_SECURITY, CS_SEC_NETWORKAUTH),
#endif
#ifdef CS_SEC_DELEGATION
    SYVAL(VAL_SECURITY, CS_SEC_DELEGATION),
#endif
#ifdef CS_SEC_MUTUALAUTH
    SYVAL(VAL_SECURITY, CS_SEC_MUTUALAUTH),
#endif
#ifdef CS_SEC_INTEGRITY
    SYVAL(VAL_SECURITY, CS_SEC_INTEGRITY),
#endif
#ifdef CS_SEC_CONFIDENTIALITY
    SYVAL(VAL_SECURITY, CS_SEC_CONFIDENTIALITY),
#endif
#ifdef CS_SEC_CREDTIMEOUT
    SYVAL(VAL_SECURITY, CS_SEC_CREDTIMEOUT),
#endif
#ifdef CS_SEC_SESSTIMEOUT
    SYVAL(VAL_SECURITY, CS_SEC_SESSTIMEOUT),
#endif
#ifdef CS_SEC_DETECTREPLAY
    SYVAL(VAL_SECURITY, CS_SEC_DETECTREPLAY),
#endif
#ifdef CS_SEC_DETECTSEQ
    SYVAL(VAL_SECURITY, CS_SEC_DETECTSEQ),
#endif
#ifdef CS_SEC_DATAORIGIN
    SYVAL(VAL_SECURITY, CS_SEC_DATAORIGIN),
#endif
#ifdef CS_SEC_MECHANISM
    SYVAL(VAL_SECURITY, CS_SEC_MECHANISM),
#endif
#ifdef CS_SEC_CHANBIND
    SYVAL(VAL_SECURITY, CS_SEC_CHANBIND),
#endif
#ifdef CS_SEC_SERVERPRINCIPAL
    SYVAL(VAL_SECURITY, CS_SEC_SERVERPRINCIPAL),
#endif
#ifdef CS_SEC_KEYTAB
    SYVAL(VAL_SECURITY, CS_SEC_KEYTAB),
#endif

#ifdef CS_SYNC_IO
    SYVAL(VAL_NETIO, CS_SYNC_IO),
#endif
#ifdef CS_ASYNC_IO
    SYVAL(VAL_NETIO, CS_ASYNC_IO),
#endif
#ifdef CS_DEFER_IO
    SYVAL(VAL_NETIO, CS_DEFER_IO),
#endif

#ifdef CS_OPT_DATEFIRST
    SYVAL(VAL_OPTION, CS_OPT_DATEFIRST),
#endif
#ifdef CS_OPT_TEXTSIZE
    SYVAL(VAL_OPTION, CS_OPT_TEXTSIZE),
#endif
#ifdef CS_OPT_STATS_TIME
    SYVAL(VAL_OPTION, CS_OPT_STATS_TIME),
#endif
#ifdef CS_OPT_STATS_IO
    SYVAL(VAL_OPTION, CS_OPT_STATS_IO),
#endif
#ifdef CS_OPT_ROWCOUNT
    SYVAL(VAL_OPTION, CS_OPT_ROWCOUNT),
#endif
#ifdef CS_OPT_NATLANG
    SYVAL(VAL_OPTION, CS_OPT_NATLANG),
#endif
#ifdef CS_OPT_DATEFORMAT
    SYVAL(VAL_OPTION, CS_OPT_DATEFORMAT),
#endif
#ifdef CS_OPT_ISOLATION
    SYVAL(VAL_OPTION, CS_OPT_ISOLATION),
#endif
#ifdef CS_OPT_AUTHON
    SYVAL(VAL_OPTION, CS_OPT_AUTHON),
#endif
#ifdef CS_OPT_CHARSET
    SYVAL(VAL_OPTION, CS_OPT_CHARSET),
#endif
#ifdef CS_OPT_SHOWPLAN
    SYVAL(VAL_OPTION, CS_OPT_SHOWPLAN),
#endif
#ifdef CS_OPT_NOEXEC
    SYVAL(VAL_OPTION, CS_OPT_NOEXEC),
#endif
#ifdef CS_OPT_ARITHIGNORE
    SYVAL(VAL_OPTION, CS_OPT_ARITHIGNORE),
#endif
#ifdef CS_OPT_TRUNCIGNORE
    SYVAL(VAL_OPTION, CS_OPT_TRUNCIGNORE),
#endif
#ifdef CS_OPT_ARITHABORT
    SYVAL(VAL_OPTION, CS_OPT_ARITHABORT),
#endif
#ifdef CS_OPT_PARSEONLY
    SYVAL(VAL_OPTION, CS_OPT_PARSEONLY),
#endif
#ifdef CS_OPT_GETDATA
    SYVAL(VAL_OPTION, CS_OPT_GETDATA),
#endif
#ifdef CS_OPT_NOCOUNT
    SYVAL(VAL_OPTION, CS_OPT_NOCOUNT),
#endif
#ifdef CS_OPT_FORCEPLAN
    SYVAL(VAL_OPTION, CS_OPT_FORCEPLAN),
#endif
#ifdef CS_OPT_FORMATONLY
    SYVAL(VAL_OPTION, CS_OPT_FORMATONLY),
#endif
#ifdef CS_OPT_CHAINXACTS
    SYVAL(VAL_OPTION, CS_OPT_CHAINXACTS),
#endif
#ifdef CS_OPT_CURCLOSEONXACT
    SYVAL(VAL_OPTION, CS_OPT_CURCLOSEONXACT),
#endif
#ifdef CS_OPT_FIPSFLAG
    SYVAL(VAL_OPTION, CS_OPT_FIPSFLAG),
#endif
#ifdef CS_OPT_RESTREES
    SYVAL(VAL_OPTION, CS_OPT_RESTREES),
#endif
#ifdef CS_OPT_IDENTITYON
    SYVAL(VAL_OPTION, CS_OPT_IDENTITYON),
#endif
#ifdef CS_OPT_CURREAD
    SYVAL(VAL_OPTION, CS_OPT_CURREAD),
#endif
#ifdef CS_OPT_CURWRITE
    SYVAL(VAL_OPTION, CS_OPT_CURWRITE),
#endif
#ifdef CS_OPT_IDENTITYOFF
    SYVAL(VAL_OPTION, CS_OPT_IDENTITYOFF),
#endif
#ifdef CS_OPT_AUTHOFF
    SYVAL(VAL_OPTION, CS_OPT_AUTHOFF),
#endif
#ifdef CS_OPT_ANSINULL
    SYVAL(VAL_OPTION, CS_OPT_ANSINULL),
#endif
#ifdef CS_OPT_QUOTED_IDENT
    SYVAL(VAL_OPTION, CS_OPT_QUOTED_IDENT),
#endif
#ifdef CS_OPT_ANSIPERM
    SYVAL(VAL_OPTION, CS_OPT_ANSIPERM),
#endif
#ifdef CS_OPT_STR_RTRUNC
    SYVAL(VAL_OPTION, CS_OPT_STR_RTRUNC),
#endif

#ifdef CS_OPT_MONDAY
    SYVAL(VAL_DATEDAY, CS_OPT_MONDAY),
#endif
#ifdef CS_OPT_TUESDAY
    SYVAL(VAL_DATEDAY, CS_OPT_TUESDAY),
#endif
#ifdef CS_OPT_WEDNESDAY
    SYVAL(VAL_DATEDAY, CS_OPT_WEDNESDAY),
#endif
#ifdef CS_OPT_THURSDAY
    SYVAL(VAL_DATEDAY, CS_OPT_THURSDAY),
#endif
#ifdef CS_OPT_FRIDAY
    SYVAL(VAL_DATEDAY, CS_OPT_FRIDAY),
#endif
#ifdef CS_OPT_SATURDAY
    SYVAL(VAL_DATEDAY, CS_OPT_SATURDAY),
#endif
#ifdef CS_OPT_SUNDAY
    SYVAL(VAL_DATEDAY, CS_OPT_SUNDAY),
#endif

#ifdef CS_OPT_FMTMDY
    SYVAL(VAL_DATEFMT, CS_OPT_FMTMDY),
#endif
#ifdef CS_OPT_FMTDMY
    SYVAL(VAL_DATEFMT, CS_OPT_FMTDMY),
#endif
#ifdef CS_OPT_FMTYMD
    SYVAL(VAL_DATEFMT, CS_OPT_FMTYMD),
#endif
#ifdef CS_OPT_FMTYDM
    SYVAL(VAL_DATEFMT, CS_OPT_FMTYDM),
#endif
#ifdef CS_OPT_FMTMYD
    SYVAL(VAL_DATEFMT, CS_OPT_FMTMYD),
#endif
#ifdef CS_OPT_FMTDYM
    SYVAL(VAL_DATEFMT, CS_OPT_FMTDYM),
#endif

#ifdef CS_HIDDEN
    SYVAL(VAL_STATUSFMT, CS_HIDDEN),
#endif
#ifdef CS_KEY
    SYVAL(VAL_STATUSFMT, CS_KEY),
#endif
#ifdef CS_VERSION_KEY
    SYVAL(VAL_STATUSFMT, CS_VERSION_KEY),
#endif
#ifdef CS_NODATA
    SYVAL(VAL_STATUSFMT, CS_NODATA),
#endif
#ifdef CS_UPDATABLE
    SYVAL(VAL_STATUSFMT, CS_UPDATABLE),
#endif
#ifdef CS_CANBENULL
    SYVAL(VAL_STATUSFMT, CS_CANBENULL),
#endif
#ifdef CS_DESCIN
    SYVAL(VAL_STATUSFMT, CS_DESCIN),
#endif
#ifdef CS_DESCOUT
    SYVAL(VAL_STATUSFMT, CS_DESCOUT),
#endif
#ifdef CS_INPUTVALUE
    SYVAL(VAL_STATUSFMT, CS_INPUTVALUE),
#endif
#ifdef CS_UPDATECOL
    SYVAL(VAL_STATUSFMT, CS_UPDATECOL),
#endif
#ifdef CS_RETURN
    SYVAL(VAL_STATUSFMT, CS_RETURN),
#endif
#ifdef CS_RETURN_CANBENULL
    SYVAL(VAL_STATUSFMT, CS_RETURN_CANBENULL),
#endif
#ifdef CS_TIMESTAMP
    SYVAL(VAL_STATUSFMT, CS_TIMESTAMP),
#endif
#ifdef CS_NODEFAULT
    SYVAL(VAL_STATUSFMT, CS_NODEFAULT),
#endif
#ifdef CS_IDENTITY
    SYVAL(VAL_STATUSFMT, CS_IDENTITY),
#endif

#ifdef CS_OPT_LEVEL0
    SYVAL(VAL_LEVEL, CS_OPT_LEVEL0),
#endif
#ifdef CS_OPT_LEVEL1
    SYVAL(VAL_LEVEL, CS_OPT_LEVEL1),
#endif
#ifdef CS_OPT_LEVEL3
    SYVAL(VAL_LEVEL, CS_OPT_LEVEL3),
#endif

#ifdef CS_CHAR_TYPE
    SYVAL(VAL_TYPE, CS_CHAR_TYPE),
#endif
#ifdef CS_BINARY_TYPE
    SYVAL(VAL_TYPE, CS_BINARY_TYPE),
#endif
#ifdef CS_LONGCHAR_TYPE
    SYVAL(VAL_TYPE, CS_LONGCHAR_TYPE),
#endif
#ifdef CS_LONGBINARY_TYPE
    SYVAL(VAL_TYPE, CS_LONGBINARY_TYPE),
#endif
#ifdef CS_TEXT_TYPE
    SYVAL(VAL_TYPE, CS_TEXT_TYPE),
#endif
#ifdef CS_IMAGE_TYPE
    SYVAL(VAL_TYPE, CS_IMAGE_TYPE),
#endif
#ifdef CS_TINYINT_TYPE
    SYVAL(VAL_TYPE, CS_TINYINT_TYPE),
#endif
#ifdef CS_SMALLINT_TYPE
    SYVAL(VAL_TYPE, CS_SMALLINT_TYPE),
#endif
#ifdef CS_INT_TYPE
    SYVAL(VAL_TYPE, CS_INT_TYPE),
#endif
#ifdef CS_REAL_TYPE
    SYVAL(VAL_TYPE, CS_REAL_TYPE),
#endif
#ifdef CS_FLOAT_TYPE
    SYVAL(VAL_TYPE, CS_FLOAT_TYPE),
#endif
#ifdef CS_BIT_TYPE
    SYVAL(VAL_TYPE, CS_BIT_TYPE),
#endif
#ifdef CS_DATETIME_TYPE
    SYVAL(VAL_TYPE, CS_DATETIME_TYPE),
#endif
#ifdef CS_DATETIME4_TYPE
    SYVAL(VAL_TYPE, CS_DATETIME4_TYPE),
#endif
#ifdef CS_DATE_TYPE
    SYVAL(VAL_TYPE, CS_DATE_TYPE),
#endif
#ifdef CS_MONEY_TYPE
    SYVAL(VAL_TYPE, CS_MONEY_TYPE),
#endif
#ifdef CS_MONEY4_TYPE
    SYVAL(VAL_TYPE, CS_MONEY4_TYPE),
#endif
#ifdef CS_NUMERIC_TYPE
    SYVAL(VAL_TYPE, CS_NUMERIC_TYPE),
#endif
#ifdef CS_DECIMAL_TYPE
    SYVAL(VAL_TYPE, CS_DECIMAL_TYPE),
#endif
#ifdef CS_VARCHAR_TYPE
    SYVAL(VAL_TYPE, CS_VARCHAR_TYPE),
#endif
#ifdef CS_VARBINARY_TYPE
    SYVAL(VAL_TYPE, CS_VARBINARY_TYPE),
#endif
#ifdef CS_LONG_TYPE
    SYVAL(VAL_TYPE, CS_LONG_TYPE),
#endif
#ifdef CS_SENSITIVITY_TYPE
    SYVAL(VAL_TYPE, CS_SENSITIVITY_TYPE),
#endif
#ifdef CS_BOUNDARY_TYPE
    SYVAL(VAL_TYPE, CS_BOUNDARY_TYPE),
#endif
#ifdef CS_VOID_TYPE
    SYVAL(VAL_TYPE, CS_VOID_TYPE),
#endif
#ifdef CS_USHORT_TYPE
    SYVAL(VAL_TYPE, CS_USHORT_TYPE),
#endif

#ifdef CS_CLIENTMSG_TYPE
    SYVAL(VAL_TYPE, CS_CLIENTMSG_TYPE),
#endif
#ifdef CS_SERVERMSG_TYPE
    SYVAL(VAL_TYPE, CS_SERVERMSG_TYPE),
#endif
#ifdef CS_ALLMSG_TYPE
    SYVAL(VAL_TYPE, CS_ALLMSG_TYPE),
#endif

#ifdef CS_SUCCEED
    SYVAL(VAL_STATUS, CS_SUCCEED),
#endif
#ifdef CS_FAIL
    SYVAL(VAL_STATUS, CS_FAIL),
#endif
#ifdef CS_MEM_ERROR
    SYVAL(VAL_STATUS, CS_MEM_ERROR),
#endif
#ifdef CS_PENDING
    SYVAL(VAL_STATUS, CS_PENDING),
#endif
#ifdef CS_QUIET
    SYVAL(VAL_STATUS, CS_QUIET),
#endif
#ifdef CS_BUSY
    SYVAL(VAL_STATUS, CS_BUSY),
#endif
#ifdef CS_INTERRUPT
    SYVAL(VAL_STATUS, CS_INTERRUPT),
#endif
#ifdef CS_BLK_HAS_TEXT
    SYVAL(VAL_STATUS, CS_BLK_HAS_TEXT),
#endif
#ifdef CS_CONTINUE
    SYVAL(VAL_STATUS, CS_CONTINUE),
#endif
#ifdef CS_FATAL
    SYVAL(VAL_STATUS, CS_FATAL),
#endif
#ifdef CS_CANCELED
    SYVAL(VAL_STATUS, CS_CANCELED),
#endif
#ifdef CS_ROW_FAIL
    SYVAL(VAL_STATUS, CS_ROW_FAIL),
#endif
#ifdef CS_END_DATA
    SYVAL(VAL_STATUS, CS_END_DATA),
#endif
#ifdef CS_END_RESULTS
    SYVAL(VAL_STATUS, CS_END_RESULTS),
#endif
#ifdef CS_END_ITEM
    SYVAL(VAL_STATUS, CS_END_ITEM),
#endif
#ifdef CS_NOMSG
    SYVAL(VAL_STATUS, CS_NOMSG),
#endif

#ifdef CS_RECOMPILE
    SYVAL(VAL_OPTION, CS_RECOMPILE),
#endif
#ifdef CS_NO_RECOMPILE
    SYVAL(VAL_OPTION, CS_NO_RECOMPILE),
#endif
#ifdef CS_BULK_INIT
    SYVAL(VAL_OPTION, CS_BULK_INIT),
#endif
#ifdef CS_BULK_CONT
    SYVAL(VAL_OPTION, CS_BULK_CONT),
#endif
#ifdef CS_BULK_DATA
    SYVAL(VAL_OPTION, CS_BULK_DATA),
#endif
#ifdef CS_COLUMN_DATA
    SYVAL(VAL_OPTION, CS_COLUMN_DATA),
#endif

#ifdef CS_FMT_UNUSED
    SYVAL(VAL_DATAFMT, CS_FMT_UNUSED),
#endif
#ifdef CS_FMT_NULLTERM
    SYVAL(VAL_DATAFMT, CS_FMT_NULLTERM),
#endif
#ifdef CS_FMT_PADNULL
    SYVAL(VAL_DATAFMT, CS_FMT_PADNULL),
#endif
#ifdef CS_FMT_PADBLANK
    SYVAL(VAL_DATAFMT, CS_FMT_PADBLANK),
#endif
#ifdef CS_FMT_JUSTIFY_RT
    SYVAL(VAL_DATAFMT, CS_FMT_JUSTIFY_RT),
#endif
#ifdef CS_FMT_STRIPBLANKS
    SYVAL(VAL_DATAFMT, CS_FMT_STRIPBLANKS),
#endif
#ifdef CS_FMT_SAFESTR
    SYVAL(VAL_DATAFMT, CS_FMT_SAFESTR),
#endif

#ifdef CS_FORCE_EXIT
    SYVAL(VAL_OPTION, CS_FORCE_EXIT),
#endif
#ifdef CS_FORCE_CLOSE
    SYVAL(VAL_OPTION, CS_FORCE_CLOSE),
#endif
#ifdef CS_INPUTVALUE
    SYVAL(VAL_OPTION, CS_INPUTVALUE),
#endif
#ifdef CS_UNUSED
    SYVAL(VAL_OPTION, CS_UNUSED),
#endif

#ifdef CS_CLIENTMSG_CB
    SYVAL(VAL_CBTYPE, CS_CLIENTMSG_CB),
#endif
#ifdef CS_COMPLETION_CB
    SYVAL(VAL_CBTYPE, CS_COMPLETION_CB),
#endif
#ifdef CS_DS_LOOKUP_CB
    SYVAL(VAL_CBTYPE, CS_DS_LOOKUP_CB),
#endif
#ifdef CS_ENCRYPT_CB
    SYVAL(VAL_CBTYPE, CS_ENCRYPT_CB),
#endif
#ifdef CS_CHALLENGE_CB
    SYVAL(VAL_CBTYPE, CS_CHALLENGE_CB),
#endif
#ifdef CS_NOTIF_CB
    SYVAL(VAL_CBTYPE, CS_NOTIF_CB),
#endif
#ifdef CS_SECSESSION_CB
    SYVAL(VAL_CBTYPE, CS_SECSESSION_CB),
#endif
#ifdef CS_SERVERMSG_CB
    SYVAL(VAL_CBTYPE, CS_SERVERMSG_CB),
#endif

#ifdef CS_TRUE
    SYVAL(VAL_RESULT, CS_TRUE),
#endif
#ifdef CS_FALSE
    SYVAL(VAL_RESULT, CS_FALSE),
#endif
#ifdef CS_MAX_PREC
    SYVAL(VAL_RESULT, CS_MAX_PREC),
#endif

#ifdef CS_CONSTAT_CONNECTED
    SYVAL(VAL_CONSTAT, CS_CONSTAT_CONNECTED),
#endif
#ifdef CS_CONSTAT_DEAD
    SYVAL(VAL_CONSTAT, CS_CONSTAT_DEAD),
#endif

#ifdef CS_CURSTAT_NONE
    SYVAL(VAL_CURSTAT, CS_CURSTAT_NONE),
#endif
#ifdef CS_CURSTAT_DECLARED
    SYVAL(VAL_CURSTAT, CS_CURSTAT_DECLARED),
#endif
#ifdef CS_CURSTAT_OPEN
    SYVAL(VAL_CURSTAT, CS_CURSTAT_OPEN),
#endif
#ifdef CS_CURSTAT_CLOSED
    SYVAL(VAL_CURSTAT, CS_CURSTAT_CLOSED),
#endif
#ifdef CS_CURSTAT_RDONLY
    SYVAL(VAL_CURSTAT, CS_CURSTAT_RDONLY),
#endif
#ifdef CS_CURSTAT_UPDATABLE
    SYVAL(VAL_CURSTAT, CS_CURSTAT_UPDATABLE),
#endif
#ifdef CS_CURSTAT_ROWCOUNT
    SYVAL(VAL_CURSTAT, CS_CURSTAT_ROWCOUNT),
#endif
#ifdef CS_CURSTAT_DEALLOC
    SYVAL(VAL_CURSTAT, CS_CURSTAT_DEALLOC),
#endif

#ifdef CS_LC_COLLATE
    SYVAL(VAL_LOCVAL, CS_LC_COLLATE),
#endif
#ifdef CS_LC_CTYPE
    SYVAL(VAL_LOCVAL, CS_LC_CTYPE),
#endif
#ifdef CS_LC_MESSAGE
    SYVAL(VAL_LOCVAL, CS_LC_MESSAGE),
#endif
#ifdef CS_LC_MONETARY
    SYVAL(VAL_LOCVAL, CS_LC_MONETARY),
#endif
#ifdef CS_LC_NUMERIC
    SYVAL(VAL_LOCVAL, CS_LC_NUMERIC),
#endif
#ifdef CS_LC_TIME
    SYVAL(VAL_LOCVAL, CS_LC_TIME),
#endif
#ifdef CS_LC_ALL
    SYVAL(VAL_LOCVAL, CS_LC_ALL),
#endif
#ifdef CS_SYB_LANG
    SYVAL(VAL_LOCVAL, CS_SYB_LANG),
#endif
#ifdef CS_SYB_CHARSET
    SYVAL(VAL_LOCVAL, CS_SYB_CHARSET),
#endif
#ifdef CS_SYB_SORTORDER
    SYVAL(VAL_LOCVAL, CS_SYB_SORTORDER),
#endif
#ifdef CS_SYB_COLLATE
    SYVAL(VAL_LOCVAL, CS_SYB_COLLATE),
#endif
#ifdef CS_SYB_LANG_CHARSET
    SYVAL(VAL_LOCVAL, CS_SYB_LANG_CHARSET),
#endif
#ifdef CS_SYB_TIME
    SYVAL(VAL_LOCVAL, CS_SYB_TIME),
#endif
#ifdef CS_SYB_MONETARY
    SYVAL(VAL_LOCVAL, CS_SYB_MONETARY),
#endif
#ifdef CS_SYB_NUMERIC
    SYVAL(VAL_LOCVAL, CS_SYB_NUMERIC),
#endif
#ifdef CS_MONTH
    SYVAL(VAL_DTINFO, CS_MONTH),
#endif
#ifdef CS_SHORTMONTH
    SYVAL(VAL_DTINFO, CS_SHORTMONTH),
#endif
#ifdef CS_DAYNAME
    SYVAL(VAL_DTINFO, CS_DAYNAME),
#endif
#ifdef CS_DATEORDER
    SYVAL(VAL_DTINFO, CS_DATEORDER),
#endif
#ifdef CS_12HOUR
    SYVAL(VAL_DTINFO, CS_12HOUR),
#endif
#ifdef CS_DT_CONVFMT
    SYVAL(VAL_DTINFO, CS_DT_CONVFMT),
#endif
#ifdef CS_DATES_SHORT
    SYVAL(VAL_CSDATES, CS_DATES_SHORT),
#endif
#ifdef CS_DATES_MDY1
    SYVAL(VAL_CSDATES, CS_DATES_MDY1),
#endif
#ifdef CS_DATES_YMD1
    SYVAL(VAL_CSDATES, CS_DATES_YMD1),
#endif
#ifdef CS_DATES_DMY1
    SYVAL(VAL_CSDATES, CS_DATES_DMY1),
#endif
#ifdef CS_DATES_DMY2
    SYVAL(VAL_CSDATES, CS_DATES_DMY2),
#endif
#ifdef CS_DATES_DMY3
    SYVAL(VAL_CSDATES, CS_DATES_DMY3),
#endif
#ifdef CS_DATES_DMY4
    SYVAL(VAL_CSDATES, CS_DATES_DMY4),
#endif
#ifdef CS_DATES_MDY2
    SYVAL(VAL_CSDATES, CS_DATES_MDY2),
#endif
#ifdef CS_DATES_HMS
    SYVAL(VAL_CSDATES, CS_DATES_HMS),
#endif
#ifdef CS_DATES_LONG
    SYVAL(VAL_CSDATES, CS_DATES_LONG),
#endif
#ifdef CS_DATES_MDY3
    SYVAL(VAL_CSDATES, CS_DATES_MDY3),
#endif
#ifdef CS_DATES_YMD2
    SYVAL(VAL_CSDATES, CS_DATES_YMD2),
#endif
#ifdef CS_DATES_YMD3
    SYVAL(VAL_CSDATES, CS_DATES_YMD3),
#endif
#ifdef CS_DATES_YDM1
    SYVAL(VAL_CSDATES, CS_DATES_YDM1),
#endif
#ifdef CS_DATES_MYD1
    SYVAL(VAL_CSDATES, CS_DATES_MYD1),
#endif
#ifdef CS_DATES_DYM1
    SYVAL(VAL_CSDATES, CS_DATES_DYM1),
#endif
#ifdef CS_DATES_SHORT_ALT
    SYVAL(VAL_CSDATES, CS_DATES_SHORT_ALT),
#endif
#ifdef CS_DATES_MDY1_YYYY
    SYVAL(VAL_CSDATES, CS_DATES_MDY1_YYYY),
#endif
#ifdef CS_DATES_YMD1_YYYY
    SYVAL(VAL_CSDATES, CS_DATES_YMD1_YYYY),
#endif
#ifdef CS_DATES_DMY1_YYYY
    SYVAL(VAL_CSDATES, CS_DATES_DMY1_YYYY),
#endif
#ifdef CS_DATES_DMY2_YYYY
    SYVAL(VAL_CSDATES, CS_DATES_DMY2_YYYY),
#endif
#ifdef CS_DATES_DMY3_YYYY
    SYVAL(VAL_CSDATES, CS_DATES_DMY3_YYYY),
#endif
#ifdef CS_DATES_DMY4_YYYY
    SYVAL(VAL_CSDATES, CS_DATES_DMY4_YYYY),
#endif
#ifdef CS_DATES_MDY2_YYYY
    SYVAL(VAL_CSDATES, CS_DATES_MDY2_YYYY),
#endif
#ifdef CS_DATES_HMS_ALT
    SYVAL(VAL_CSDATES, CS_DATES_HMS_ALT),
#endif
#ifdef CS_DATES_LONG_ALT
    SYVAL(VAL_CSDATES, CS_DATES_LONG_ALT),
#endif
#ifdef CS_DATES_MDY3_YYYY
    SYVAL(VAL_CSDATES, CS_DATES_MDY3_YYYY),
#endif
#ifdef CS_DATES_YMD2_YYYY
    SYVAL(VAL_CSDATES, CS_DATES_YMD2_YYYY),
#endif
#ifdef CS_DATES_YMD3_YYYY
    SYVAL(VAL_CSDATES, CS_DATES_YMD3_YYYY),
#endif
    {0,0,0}
};

char *mask_str(int type, int value)
{
    value_desc *desc;
    static char str[1024];
    int i;

    i = 0;
    for (desc = sybase_args; desc->name != NULL; desc++)
	if (desc->type == type) {
	    int match = 0;

	    if (value == 0) {
		if (desc->value == 0)
		    match = 1;
	    } else if ((value & desc->value) != 0)
		match = 1;
	    if (match) {
		if (i > 0)
		    str[i++] = '+';
		strcpy(str + i, desc->name);
		i += strlen(str);
	    }
	}
    if (i == 0)
	str[i++] = '0';
    str[i] = '\0';
    return str;
}

char *value_str(int type, int value)
{
    value_desc *desc;
    char *name = NULL;
    static char num_str[16];

    for (desc = sybase_args; desc->name != NULL; desc++)
	if (desc->value == value) {
	    if (desc->type == type)
		return desc->name;
	    name = desc->name;
	}
    if (name != NULL)
	return name;
    sprintf(num_str, "%d", value);
    return num_str;
}

static int dict_add_int(PyObject *dict, char *name, int value)
{
    int status;
    PyObject *obj = PyInt_FromLong(value);
    if (obj == NULL)
	return -1;

    status = PyDict_SetItemString(dict, name, obj);
    Py_DECREF(obj);
    return status;
}

static int dict_add_type(PyObject *dict, PyTypeObject *type)
{
    return PyDict_SetItemString(dict, type->tp_name, (PyObject*)type);
}

void initsybasect(void)
{
    PyObject *m, *d, *rev = NULL;
    value_desc *desc;

#ifdef HAVE_DECIMAL
    PyObject *builtins = NULL, *list = NULL, *empty_dict = NULL,
      *__import__ = NULL, *decimal = NULL, *Decimal = NULL, *mod = NULL;
#endif

    /* Initialise the type of the new type objects here; doing it here
     * is required for portability to Windows without requiring C++. */
#ifdef WANT_BULKCOPY
    CS_BLKDESCType.ob_type = &PyType_Type;
#endif
    CS_COMMANDType.ob_type = &PyType_Type;
    CS_CONNECTIONType.ob_type = &PyType_Type;
    CS_CONTEXTType.ob_type = &PyType_Type;
    CS_DATAFMTType.ob_type = &PyType_Type;
    CS_IODESCType.ob_type = &PyType_Type;
    CS_LOCALEType.ob_type = &PyType_Type;
    CS_CLIENTMSGType.ob_type = &PyType_Type;
    CS_SERVERMSGType.ob_type = &PyType_Type;
    NumericType.ob_type = &PyType_Type;
    DateTimeType.ob_type = &PyType_Type;
#ifdef CS_DATE_TYPE
    DateType.ob_type = &PyType_Type;
#endif
    MoneyType.ob_type = &PyType_Type;
    DataBufType.ob_type = &PyType_Type;

    /* Create the module and add the functions */
    m = Py_InitModule4(module, sybasect_methods,
		       sybasect_module_documentation,
		       (PyObject*)NULL, PYTHON_API_VERSION);
    if (m == NULL)
	goto error;

    /* Add some symbolic constants to the module */
    d = PyModule_GetDict(m);
    if (d == NULL)
	goto error;
    /* Add constants */
    for (desc = sybase_args; desc->name != NULL; desc++)
	if (dict_add_int(d, desc->name, desc->value) < 0)
	    goto error;

#ifdef WANT_THREADS
    if (dict_add_int(d, "__with_threads__", 1) < 0)
	goto error;
#else
    if (dict_add_int(d, "__with_threads__", 0) < 0)
	goto error;
#endif

#ifdef HAVE_DATETIME
    PyDateTime_IMPORT;
    if (PyErr_Occurred())
        goto error;
#endif

#ifdef HAVE_DECIMAL
    builtins = PyImport_AddModule("__builtin__"); if (!builtins) goto error;
    __import__ = PyObject_GetAttrString(builtins, "__import__"); if (!__import__) goto error;
    Decimal = PyString_FromString("Decimal"); if (!Decimal) goto error;
    list = PyList_New(1); if (!list) goto error;
    Py_INCREF(Decimal);
    PyList_SET_ITEM(list, 0, Decimal);
    empty_dict = PyDict_New(); if (!empty_dict) goto error;
    decimal = PyString_FromString("decimal"); if (!decimal) goto error;
    mod = PyObject_CallFunction(__import__, "OOOO", decimal, d, empty_dict, list);
    DecimalClass = PyObject_GetAttr(mod, Decimal); if (!DecimalClass) goto error;
#endif

#ifdef HAVE_FREETDS
    if (dict_add_int(d, "__have_freetds__", HAVE_FREETDS) < 0)
	goto error;
#else
    if (dict_add_int(d, "__have_freetds__", 0) < 0)
	goto error;
#endif


    if ((rev = PyString_FromString("0.39")) == NULL)
	goto error;
    if (PyDict_SetItemString(d, "__version__", rev) < 0)
	goto error;

    /* Set debug file to None */
    debug_file = Py_None;
    Py_INCREF(debug_file);

    /* Add type objects */
    if (dict_add_type(d, &CS_COMMANDType)
#ifdef WANT_BULKCOPY
	|| dict_add_type(d, &CS_BLKDESCType)
#endif
	|| dict_add_type(d, &CS_CONNECTIONType)
	|| dict_add_type(d, &CS_CONTEXTType)
	|| dict_add_type(d, &CS_DATAFMTType)
	|| dict_add_type(d, &CS_IODESCType)
	|| dict_add_type(d, &CS_CLIENTMSGType)
	|| dict_add_type(d, &CS_SERVERMSGType)
	|| dict_add_type(d, &CS_LOCALEType)
	|| dict_add_type(d, &NumericType)
	|| dict_add_type(d, &MoneyType)
	|| dict_add_type(d, &DateTimeType)
#ifdef CS_DATE_TYPE
	|| dict_add_type(d, &DateType)
#endif
	|| dict_add_type(d, &DataBufType)

	/* Register pickler functions */
	|| copy_reg_numeric(d)
	|| copy_reg_money(d)
	|| copy_reg_datetime(d)
#ifdef CS_DATE_TYPE
	|| copy_reg_date(d)
#endif
	);



error:
    Py_XDECREF(rev);

#ifdef HAVE_DECIMAL
    Py_XDECREF(__import__);
    Py_XDECREF(list);
    Py_XDECREF(Decimal);
    Py_XDECREF(empty_dict);
    Py_XDECREF(decimal);
    Py_XDECREF(mod);
#endif

    /* Check for errors */
    if (PyErr_Occurred()) {
	char msg[128];

	sprintf(msg, "%s: import failed", module);
	Py_FatalError(msg);
    }
}
