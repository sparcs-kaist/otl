/******************************************************************

 Copyright 2001 by Object Craft P/L, Melbourne, Australia.

 LICENCE - see LICENCE file distributed with this software for details.

******************************************************************/

#include "sybasect.h"

static CS_CONNECTIONObj *conn_list;

static void conn_add_object(CS_CONNECTIONObj *conn)
{
    conn->next = conn_list;
    conn_list = conn;
}

static void conn_del_object(CS_CONNECTIONObj *conn)
{
    CS_CONNECTIONObj *scan, *prev;

    for (prev = NULL, scan = conn_list; scan != NULL; scan = scan->next) {
	if (scan == conn) {
	    if (prev == NULL)
		conn_list = scan->next;
	    else
		prev->next = scan->next;
	}
    }
}

PyObject *conn_find_object(CS_CONNECTION *cs_conn)
{
    CS_CONNECTIONObj *conn;

    for (conn = conn_list; conn != NULL; conn = conn->next)
	if (conn->conn == cs_conn)
	    return (PyObject*)conn;
    return NULL;
}

static char CS_CONNECTION_ct_diag__doc__[] = 
"ct_diag(CS_INIT) -> status\n"
"ct_diag(CS_MSGLIMIT, type, num) -> status\n"
"ct_diag(CS_CLEAR, type) -> status\n"
"ct_diag(CS_GET, type, index) -> status, msg\n"
"ct_diag(CS_STATUS, type) -> status, num\n"
"ct_diag(CS_EED_CMD, type, index) -> status, cmd";

static PyObject *CS_CONNECTION_ct_diag(CS_CONNECTIONObj *self, PyObject *args)
{
    int operation, type, index, num;
    CS_VOID *buffer;
    PyObject *msg;
    CS_RETCODE status;
#ifndef HAVE_FREETDS
    PyObject *cmd;
    CS_COMMAND *eed;
#endif

    if (!first_tuple_int(args, &operation))
	return NULL;

    if (self->conn == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_CONNECTION has been dropped");
	return NULL;
    }

    switch (operation) {
    case CS_INIT:
	/* ct_diag(CS_INIT) -> status */
	if (!PyArg_ParseTuple(args, "i", &operation))
	    return NULL;

	/* PyErr_Clear(); */

#ifdef HAVE_FREETDS
	status = CS_SUCCEED;
#else
	SY_CONN_BEGIN_THREADS(self);
	status = ct_diag(self->conn, operation, CS_UNUSED, CS_UNUSED, NULL);
	SY_CONN_END_THREADS(self);
#endif

	if (self->debug)
	    debug_msg("ct_diag(conn%d, CS_INIT, CS_UNUSED, CS_UNUSED, NULL)"
		      " -> %s\n",
		      self->serial, value_str(VAL_STATUS, status));
	if (PyErr_Occurred())
	    return NULL;

	return PyInt_FromLong(status);

    case CS_MSGLIMIT:
	/* ct_diag(CS_MSGLIMIT, type, num) -> status */
	if (!PyArg_ParseTuple(args, "iii", &operation, &type, &num))
	    return NULL;

	/* PyErr_Clear(); */

#ifdef HAVE_FREETDS
	status = CS_SUCCEED;
#else
	SY_CONN_BEGIN_THREADS(self);
	status = ct_diag(self->conn, operation, type, CS_UNUSED, &num);
	SY_CONN_END_THREADS(self);
#endif

	if (self->debug)
	    debug_msg("ct_diag(conn%d, CS_MSGLIMIT, %s, CS_UNUSED, %d)"
		      " -> %s\n",
		      self->serial, value_str(VAL_TYPE, type), num,
		      value_str(VAL_STATUS, status));
	if (PyErr_Occurred())
	    return NULL;

	return PyInt_FromLong(status);

    case CS_CLEAR:
	/* ct_diag(CS_CLEAR, type) -> status */
	if (!PyArg_ParseTuple(args, "ii", &operation, &type))
	    return NULL;

	/* PyErr_Clear(); */

#ifdef HAVE_FREETDS
	status = CS_SUCCEED;
#else
	SY_CONN_BEGIN_THREADS(self);
	status = ct_diag(self->conn, operation, type, CS_UNUSED, NULL);
	SY_CONN_END_THREADS(self);
#endif

	if (self->debug)
	    debug_msg("ct_diag(conn%d, CS_CLEAR, %s, CS_UNUSED, NULL) -> %s\n",
		      self->serial, value_str(VAL_TYPE, type),
		      value_str(VAL_STATUS, status));
	if (PyErr_Occurred())
	    return NULL;

	return PyInt_FromLong(status);

    case CS_GET:
	/* ct_diag(CS_GET, type, index) -> status, msg */
	if (!PyArg_ParseTuple(args, "iii", &operation, &type, &index))
	    return NULL;
	if (type == CS_CLIENTMSG_TYPE) {
	    if ((msg = clientmsg_alloc()) == NULL)
		return NULL;
	    buffer = &((CS_CLIENTMSGObj*)msg)->msg;
	} else if (type == CS_SERVERMSG_TYPE) {
	    if ((msg = servermsg_alloc()) == NULL)
		return NULL;
	    buffer = &((CS_SERVERMSGObj*)msg)->msg;
	} else {
	    PyErr_SetString(PyExc_TypeError, "unsupported message type");
	    return NULL;
	}

	/* PyErr_Clear(); */

#ifdef HAVE_FREETDS
	status = CS_SUCCEED;
#else
	SY_CONN_BEGIN_THREADS(self);
	status = ct_diag(self->conn, operation, type, index, buffer);
	SY_CONN_END_THREADS(self);
#endif

	if (self->debug)
	    debug_msg("ct_diag(conn%d, CS_GET, %s, %d, buff) -> %s\n",
		      self->serial, value_str(VAL_TYPE, type), index,
		      value_str(VAL_STATUS, status));
	if (PyErr_Occurred()) {
	    Py_DECREF(msg);
	    return NULL;
	}

	if (status != CS_SUCCEED) {
	    Py_DECREF(msg);
	    return Py_BuildValue("iO", status, Py_None);
	}
	return Py_BuildValue("iN", CS_SUCCEED, msg);

    case CS_STATUS:
	/* ct_diag(CS_STATUS, type) -> status, num */
	if (!PyArg_ParseTuple(args, "ii", &operation, &type))
	    return NULL;
	num = 0;

	/* PyErr_Clear(); */

#ifdef HAVE_FREETDS
	status = CS_SUCCEED;
#else
	SY_CONN_BEGIN_THREADS(self);
	status = ct_diag(self->conn, operation, type, CS_UNUSED, &num);
	SY_CONN_END_THREADS(self);
#endif

	if (self->debug)
	    debug_msg("ct_diag(conn%d, CS_STATUS, %s, CS_UNUSED, &num)"
		      " -> %s, %d\n",
		      self->serial, value_str(VAL_TYPE, type),
		      value_str(VAL_STATUS, status), num);
	if (PyErr_Occurred())
	    return NULL;

	return Py_BuildValue("ii", status, num);

#ifndef HAVE_FREETDS
    case CS_EED_CMD:
	/* ct_diag(CS_EED_CMD, type, index) -> status, cmd */
	if (!PyArg_ParseTuple(args, "iii", &operation, &type, &index))
	    return NULL;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self);
	status = ct_diag(self->conn, operation, type, index, &eed);
	SY_CONN_END_THREADS(self);

	if (self->debug)
	    debug_msg("ct_diag(conn%d, CS_EED_CMD, %s, %d, &eed) -> %s",
		      self->serial, value_str(VAL_TYPE, type), index,
		      value_str(VAL_STATUS, status));
	if (PyErr_Occurred()) {
	    if (self->debug)
		debug_msg("\n");
	    return NULL;
	}

	cmd = cmd_eed(self, eed);
	if (cmd == NULL) {
	    if (self->debug)
		debug_msg("\n");
	    return NULL;
	}
	if (self->debug)
	    debug_msg(", cmd%d\n", ((CS_COMMANDObj*)cmd)->serial);
	return Py_BuildValue("iN", status, cmd);
#endif

    default:
	PyErr_SetString(PyExc_TypeError, "unknown operation");
	return NULL;
    }
}

static char CS_CONNECTION_ct_cancel__doc__[] = 
"ct_cancel(type) -> status";

static PyObject *CS_CONNECTION_ct_cancel(CS_CONNECTIONObj *self, PyObject *args)
{
    int type;
    CS_RETCODE status;

    if (!PyArg_ParseTuple(args, "i", &type))
	return NULL;

    if (self->conn == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_CONNECTION has been dropped");
	return NULL;
    }

    /* PyErr_Clear(); */

    SY_CONN_BEGIN_THREADS(self);
    status = ct_cancel(self->conn, NULL, type);
    SY_CONN_END_THREADS(self);

    if (self->debug)
	debug_msg("ct_cancel(conn%d, NULL, %s) -> %s\n",
		  self->serial, value_str(VAL_CANCEL, type),
		  value_str(VAL_STATUS, status));
    if (PyErr_Occurred())
	return NULL;

    return PyInt_FromLong(status);
}

static char CS_CONNECTION_ct_connect__doc__[] = 
"ct_connect(str = None) - > status";

static PyObject *CS_CONNECTION_ct_connect(CS_CONNECTIONObj *self, PyObject *args)
{
    CS_RETCODE status;
    char *dsn = NULL;

    if (!PyArg_ParseTuple(args, "|s", &dsn))
	return NULL;

    if (self->conn == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_CONNECTION has been dropped");
	return NULL;
    }

    /* PyErr_Clear(); */
    if (dsn == NULL) {
	SY_CONN_BEGIN_THREADS(self);
	status = ct_connect(self->conn, NULL, 0);
	SY_CONN_END_THREADS(self);

	if (self->debug)
	    debug_msg("ct_connect(conn%d, NULL, 0) -> %s\n",
		      self->serial, value_str(VAL_STATUS, status));
    } else {
	SY_CONN_BEGIN_THREADS(self);
	status = ct_connect(self->conn, dsn, CS_NULLTERM);
	SY_CONN_END_THREADS(self);

	if (self->debug)
	    debug_msg("ct_connect(conn%d, \"%s\", CS_NULLTERM) -> %s\n",
		      self->serial, dsn, value_str(VAL_STATUS, status));
    }
    if (PyErr_Occurred())
	return NULL;

    return PyInt_FromLong(status);
}

static char CS_CONNECTION_ct_cmd_alloc__doc__[] = 
"ct_cmd_alloc() -> status, cmd";

static PyObject *CS_CONNECTION_ct_cmd_alloc(CS_CONNECTIONObj *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ""))
	return NULL;

    if (self->conn == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_CONNECTION has been dropped");
	return NULL;
    }

    return cmd_alloc(self);
}

#ifdef WANT_BULKCOPY
static char CS_CONNECTION_blk_alloc__doc__[] = 
"blk_alloc([version = BLK_VERSION_100) -> status, blk";

static PyObject *CS_CONNECTION_blk_alloc(CS_CONNECTIONObj *self, PyObject *args)
{
    int version = BLK_VERSION_100;

    if (!PyArg_ParseTuple(args, "|i", &version))
	return NULL;

    if (self->conn == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_CONNECTION has been dropped");
	return NULL;
    }

    return bulk_alloc(self, version);
}
#endif

static char CS_CONNECTION_ct_close__doc__[] = 
"ct_close([option]) - > status";

static PyObject *CS_CONNECTION_ct_close(CS_CONNECTIONObj *self, PyObject *args)
{
    CS_RETCODE status;
    int option = CS_UNUSED;

    if (!PyArg_ParseTuple(args, "|i", &option))
	return NULL;
    
    if (self->conn == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_CONNECTION has been dropped");
	return NULL;
    }

    /* PyErr_Clear(); */

    SY_CONN_BEGIN_THREADS(self);
    status = ct_close(self->conn, option);
    SY_CONN_END_THREADS(self);

    if (self->debug)
	debug_msg("ct_close(conn%d, %s) -> %s\n",
		  self->serial, value_str(VAL_OPTION, option),
		  value_str(VAL_STATUS, status));
    if (PyErr_Occurred())
	return NULL;

    return PyInt_FromLong(status);
}

static char CS_CONNECTION_ct_con_drop__doc__[] = 
"ct_con_drop() - > status";

static PyObject *CS_CONNECTION_ct_con_drop(CS_CONNECTIONObj *self, PyObject *args)
{
    CS_RETCODE status;

    if (!PyArg_ParseTuple(args, ""))
	return NULL;
    
    if (self->conn == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_CONNECTION has been dropped");
	return NULL;
    }

    /* PyErr_Clear(); */

    SY_CONN_BEGIN_THREADS(self);
    status = ct_con_drop(self->conn);
    SY_CONN_END_THREADS(self);

    if (self->debug)
	debug_msg("ct_con_drop(conn%d) -> %s\n",
		  self->serial, value_str(VAL_STATUS, status));
    if (status == CS_SUCCEED)
	self->conn = NULL;

    if (PyErr_Occurred())
	return NULL;

    return PyInt_FromLong(status);
}

static int property_type(int property)
{
    switch (property) {
#ifdef CS_ANSI_BINDS
    case CS_ANSI_BINDS:
#endif
#ifdef CS_ASYNC_NOTIFS
    case CS_ASYNC_NOTIFS:
#endif
#ifdef CS_BULK_LOGIN
    case CS_BULK_LOGIN:
#endif
#ifdef CS_CHARSETCNV
    case CS_CHARSETCNV:
#endif
#ifdef CS_CONFIG_BY_SERVERNAME
    case CS_CONFIG_BY_SERVERNAME:
#endif
#ifdef CS_DIAG_TIMEOUT
    case CS_DIAG_TIMEOUT:
#endif
#ifdef CS_DISABLE_POLL
    case CS_DISABLE_POLL:
#endif
#ifdef CS_DS_COPY
    case CS_DS_COPY:
#endif
#ifdef CS_DS_EXPANDALIAS
    case CS_DS_EXPANDALIAS:
#endif
#ifdef CS_DS_FAILOVER
    case CS_DS_FAILOVER:
#endif
#ifdef CS_EXPOSE_FMTS
    case CS_EXPOSE_FMTS:
#endif
#ifdef CS_EXTERNAL_CONFIG
    case CS_EXTERNAL_CONFIG:
#endif
#ifdef CS_EXTRA_INF
    case CS_EXTRA_INF:
#endif
#ifdef CS_HIDDEN_KEYS
    case CS_HIDDEN_KEYS:
#endif
#ifdef CS_LOGIN_STATUS
    case CS_LOGIN_STATUS:
#endif
#ifdef CS_NOCHARSETCNV_REQD
    case CS_NOCHARSETCNV_REQD:
#endif
#ifdef CS_SEC_APPDEFINED
    case CS_SEC_APPDEFINED:
#endif
#ifdef CS_SEC_CHALLENGE
    case CS_SEC_CHALLENGE:
#endif
#ifdef CS_SEC_CHANBIND
    case CS_SEC_CHANBIND:
#endif
#ifdef CS_SEC_CONFIDENTIALITY
    case CS_SEC_CONFIDENTIALITY:
#endif
#ifdef CS_SEC_DATAORIGIN
    case CS_SEC_DATAORIGIN:
#endif
#ifdef CS_SEC_DELEGATION
    case CS_SEC_DELEGATION:
#endif
#ifdef CS_SEC_DETECTREPLAY
    case CS_SEC_DETECTREPLAY:
#endif
#ifdef CS_SEC_DETECTSEQ
    case CS_SEC_DETECTSEQ:
#endif
#ifdef CS_SEC_ENCRYPTION
    case CS_SEC_ENCRYPTION:
#endif
#ifdef CS_SEC_INTEGRITY
    case CS_SEC_INTEGRITY:
#endif
#ifdef CS_SEC_MUTUALAUTH
    case CS_SEC_MUTUALAUTH:
#endif
#ifdef CS_SEC_NEGOTIATE
    case CS_SEC_NEGOTIATE:
#endif
#ifdef CS_SEC_NETWORKAUTH
    case CS_SEC_NETWORKAUTH:
#endif
	return OPTION_BOOL;
#ifdef CS_CON_STATUS
    case CS_CON_STATUS:
#endif
#ifdef CS_LOOP_DELAY
    case CS_LOOP_DELAY:
#endif
#ifdef CS_RETRY_COUNT
    case CS_RETRY_COUNT:
#endif
#ifdef CS_NETIO
    case CS_NETIO:
#endif
#ifdef CS_TEXTLIMIT
    case CS_TEXTLIMIT:
#endif
#ifdef CS_DS_SEARCH
    case CS_DS_SEARCH:
#endif
#ifdef CS_DS_SIZELIMIT
    case CS_DS_SIZELIMIT:
#endif
#ifdef CS_DS_TIMELIMIT
    case CS_DS_TIMELIMIT:
#endif
#ifdef CS_ENDPOINT
    case CS_ENDPOINT:
#endif
#ifdef CS_PACKETSIZE
    case CS_PACKETSIZE:
#endif
#ifdef CS_SEC_CREDTIMEOUT
    case CS_SEC_CREDTIMEOUT:
#endif
#ifdef CS_SEC_SESSTIMEOUT
    case CS_SEC_SESSTIMEOUT:
#endif
#ifdef CS_TDS_VERSION
    case CS_TDS_VERSION:
#endif
	return OPTION_INT;
#ifdef CS_APPNAME
    case CS_APPNAME:
#endif
#ifdef CS_HOSTNAME
    case CS_HOSTNAME:
#endif
#ifdef CS_PASSWORD
    case CS_PASSWORD:
#endif
#ifdef CS_SERVERNAME
    case CS_SERVERNAME:
#endif
#ifdef CS_USERNAME
    case CS_USERNAME:
#endif
#ifdef CS_DS_DITBASE
    case CS_DS_DITBASE:
#endif
#ifdef CS_DS_PASSWORD
    case CS_DS_PASSWORD:
#endif
#ifdef CS_DS_PRINCIPAL
    case CS_DS_PRINCIPAL:
#endif
#ifdef CS_DS_PROVIDER
    case CS_DS_PROVIDER:
#endif
#ifdef CS_SEC_KEYTAB
    case CS_SEC_KEYTAB:
#endif
#ifdef CS_SEC_MECHANISM
    case CS_SEC_MECHANISM:
#endif
#ifdef CS_SEC_SERVERPRINCIPAL
    case CS_SEC_SERVERPRINCIPAL:
#endif
#ifdef CS_TRANSACTION_NAME
    case CS_TRANSACTION_NAME:
#endif
	return OPTION_STRING;
#ifdef CS_LOC_PROP
    case CS_LOC_PROP:
	return OPTION_LOCALE;
#endif
#ifdef CS_EED_CMD
    case CS_EED_CMD:
	return OPTION_CMD;
#endif
    default:
	return OPTION_UNKNOWN;
    }
}

static char CS_CONNECTION_ct_con_props__doc__[] = 
"ct_con_props(CS_SET, property, value) -> status\n"
"ct_con_props(CS_GET, property) -> status, value\n"
#ifdef CS_CLEAR
"ct_con_props(CS_CLEAR, property) -> status\n"
#endif
;

static PyObject *CS_CONNECTION_ct_con_props(CS_CONNECTIONObj *self, PyObject *args)
{
    int action, property;
    PyObject *obj = NULL;
    CS_RETCODE status;
    CS_INT int_value;
    CS_BOOL bool_value;
    char *str_value;
    char str_buff[10240];
    CS_INT buff_len;

    if (!first_tuple_int(args, &action))
	return NULL;

    if (self->conn == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_CONNECTION has been dropped");
	return NULL;
    }

    switch (action) {
    case CS_SET:
	/* ct_con_props(CS_SET, property, value) -> status */
	if (!PyArg_ParseTuple(args, "iiO", &action, &property, &obj))
	    return NULL;

	switch (property_type(property)) {
	case OPTION_BOOL:
	    bool_value = PyInt_AsLong(obj);
	    if (PyErr_Occurred())
		return NULL;

	    /* PyErr_Clear(); */

	    SY_CONN_BEGIN_THREADS(self);
	    status = ct_con_props(self->conn, CS_SET, property,
				  &bool_value, CS_UNUSED, NULL);
	    SY_CONN_END_THREADS(self);

	    if (self->debug)
		debug_msg("ct_con_props(conn%d, CS_SET, %s, %d, CS_UNUSED,"
			  " NULL) -> %s\n",
			  self->serial,
			  value_str(VAL_PROPS, property), (int)bool_value,
			  value_str(VAL_STATUS, status));
	    if (PyErr_Occurred())
		return NULL;

	    return PyInt_FromLong(status);

	case OPTION_INT:
	    int_value = PyInt_AsLong(obj);
	    if (PyErr_Occurred())
		return NULL;

	    /* PyErr_Clear(); */

	    SY_CONN_BEGIN_THREADS(self);
	    status = ct_con_props(self->conn, CS_SET, property,
				  &int_value, CS_UNUSED, NULL);
	    SY_CONN_END_THREADS(self);

	    if (self->debug)
		debug_msg("ct_con_props(conn%d, CS_SET, %s, %d, CS_UNUSED,"
			  " NULL) -> %s\n",
			  self->serial,
			  value_str(VAL_PROPS, property), (int)int_value,
			  value_str(VAL_STATUS, status));
	    if (PyErr_Occurred())
		return NULL;

	    return PyInt_FromLong(status);

	case OPTION_STRING:
	    str_value = PyString_AsString(obj);
	    if (PyErr_Occurred())
		return NULL;

	    /* PyErr_Clear(); */

	    SY_CONN_BEGIN_THREADS(self);
	    status = ct_con_props(self->conn, CS_SET, property,
				  str_value, CS_NULLTERM, NULL);
	    SY_CONN_END_THREADS(self);

	    if (self->debug)
		debug_msg("ct_con_props(conn%d, CS_SET, %s, \"%s\","
			  " CS_NULLTERM, NULL) -> %s\n",
			  self->serial,
			  value_str(VAL_PROPS, property), str_value,
			  value_str(VAL_STATUS, status));
	    if (PyErr_Occurred())
		return NULL;

	    return PyInt_FromLong(status);

	case OPTION_LOCALE:
	    if (!CS_LOCALE_Check(obj)) {
		PyErr_SetString(PyExc_TypeError, "CS_LOCALE is required");
		return NULL;
	    }

	    /* PyErr_Clear(); */

	    SY_CONN_BEGIN_THREADS(self);
	    status = ct_con_props(self->conn, CS_SET, property,
				  ((CS_LOCALEObj*)obj)->locale, CS_UNUSED, NULL);
	    SY_CONN_END_THREADS(self);

	    if (self->debug)
		debug_msg("ct_con_props(conn%d, CS_SET, %s, locale%d,"
			  " CS_UNUSED, NULL) -> %s\n",
			  self->serial, value_str(VAL_PROPS, property),
			  ((CS_LOCALEObj*)obj)->serial,
			  value_str(VAL_STATUS, status));
	    if (PyErr_Occurred())
		return NULL;

	    return PyInt_FromLong(status);

	default:
	    PyErr_SetString(PyExc_TypeError, "unhandled property value");
	    return NULL;
	}
	break;

    case CS_GET:
	/* ct_con_props(CS_GET, property) -> status, value */
	if (!PyArg_ParseTuple(args, "ii", &action, &property))
	    return NULL;

	switch (property_type(property)) {
	case OPTION_BOOL:
	    /* PyErr_Clear(); */

	    SY_CONN_BEGIN_THREADS(self);
	    status = ct_con_props(self->conn, CS_GET, property,
				  &bool_value, CS_UNUSED, NULL);
	    SY_CONN_END_THREADS(self);

	    if (self->debug)
		debug_msg("ct_con_props(conn%d, CS_GET, %s, &value, CS_UNUSED,"
			  " NULL) -> %s, %d\n",
			  self->serial,
			  value_str(VAL_PROPS, property),
			  value_str(VAL_STATUS, status), (int)bool_value);
	    if (PyErr_Occurred())
		return NULL;

	    return Py_BuildValue("ii", status, bool_value);

	case OPTION_INT:
	    /* PyErr_Clear(); */

	    SY_CONN_BEGIN_THREADS(self);
	    status = ct_con_props(self->conn, CS_GET, property,
				  &int_value, CS_UNUSED, NULL);
	    SY_CONN_END_THREADS(self);

	    if (self->debug) {
#ifdef CS_LOGIN_STATUS
		if (property == CS_CON_STATUS || property == CS_LOGIN_STATUS)
#else
		if (property == CS_CON_STATUS)
#endif
		    debug_msg("ct_con_props(conn%d, CS_GET, %s, &value,"
			      " CS_UNUSED, NULL) -> %s, %s\n",
			      self->serial,
			      value_str(VAL_PROPS, property),
			      value_str(VAL_STATUS, status),
			      mask_str(VAL_CONSTAT, (int)int_value));
		else
		    debug_msg("ct_con_props(conn%d, CS_GET, %s, &value,"
			      " CS_UNUSED, NULL) -> %s, %d\n",
			      self->serial,
			      value_str(VAL_PROPS, property),
			      value_str(VAL_STATUS, status), (int)int_value);
	    }
	    if (PyErr_Occurred())
		return NULL;

	    return Py_BuildValue("ii", status, int_value);

	case OPTION_STRING:
	    /* PyErr_Clear(); */

	    SY_CONN_BEGIN_THREADS(self);
	    status = ct_con_props(self->conn, CS_GET, property,
				  str_buff, sizeof(str_buff), &buff_len);
	    SY_CONN_END_THREADS(self);

	    if (buff_len > sizeof(str_buff))
		buff_len = sizeof(str_buff);
	    if (self->debug)
		debug_msg("ct_con_props(conn%d, CS_GET, %s, buff, %d, &outlen)"
			  " -> %s, '%.*s'\n",
			  self->serial,
			  value_str(VAL_PROPS, property), sizeof(str_buff),
			  value_str(VAL_STATUS, status), (int)buff_len, str_buff);
	    if (PyErr_Occurred())
		return NULL;

	    return Py_BuildValue("is", status, str_buff);

	case OPTION_CMD:
	    PyErr_SetString(PyExc_TypeError, "EED not supported yet");
	    return NULL;

	case OPTION_LOCALE:
	    PyErr_SetString(PyExc_TypeError, "LOCALE not supported yet");
	    return NULL;

	case OPTION_UNKNOWN:
	    PyErr_SetString(PyExc_TypeError, "unknown property value");
	    return NULL;

	default:
	    PyErr_SetString(PyExc_TypeError, "unhandled property value");
	    return NULL;
	}
	break;

#ifdef CS_CLEAR
    case CS_CLEAR:
	/* ct_con_props(CS_CLEAR, property) -> status */
	if (!PyArg_ParseTuple(args, "ii", &action, &property))
	    return NULL;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self);
	status = ct_con_props(self->conn, CS_CLEAR, property,
			      NULL, CS_UNUSED, NULL);
	SY_CONN_END_THREADS(self);

	if (self->debug)
	    debug_msg("ct_con_props(conn%d, CS_CLEAR, %s, NULL, CS_UNUSED,"
		      " NULL) -> %s\n",
		      self->serial,
		      value_str(VAL_PROPS, property),
		      value_str(VAL_STATUS, status));
	if (PyErr_Occurred())
	    return NULL;

	return PyInt_FromLong(status);
#endif

    default:
	PyErr_SetString(PyExc_TypeError, "unknown action");
	return NULL;
    }
}

static int option_type(int option)
{
    switch (option) {
#ifdef CS_OPT_ANSINULL
    case CS_OPT_ANSINULL:
#endif
#ifdef CS_OPT_ANSIPERM
    case CS_OPT_ANSIPERM:
#endif
#ifdef CS_OPT_ARITHABORT
    case CS_OPT_ARITHABORT:
#endif
#ifdef CS_OPT_ARITHIGNORE
    case CS_OPT_ARITHIGNORE:
#endif
#ifdef CS_OPT_CHAINXACTS
    case CS_OPT_CHAINXACTS:
#endif
#ifdef CS_OPT_CURCLOSEONXACT
    case CS_OPT_CURCLOSEONXACT:
#endif
#ifdef CS_OPT_FIPSFLAG
    case CS_OPT_FIPSFLAG:
#endif
#ifdef CS_OPT_FORCEPLAN
    case CS_OPT_FORCEPLAN:
#endif
#ifdef CS_OPT_FORMATONLY
    case CS_OPT_FORMATONLY:
#endif
#ifdef CS_OPT_GETDATA
    case CS_OPT_GETDATA:
#endif
#ifdef CS_OPT_NOCOUNT
    case CS_OPT_NOCOUNT:
#endif
#ifdef CS_OPT_NOEXEC
    case CS_OPT_NOEXEC:
#endif
#ifdef CS_OPT_PARSEONLY
    case CS_OPT_PARSEONLY:
#endif
#ifdef CS_OPT_QUOTED_IDENT
    case CS_OPT_QUOTED_IDENT:
#endif
#ifdef CS_OPT_RESTREES
    case CS_OPT_RESTREES:
#endif
#ifdef CS_OPT_SHOWPLAN
    case CS_OPT_SHOWPLAN:
#endif
#ifdef CS_OPT_STATS_IO
    case CS_OPT_STATS_IO:
#endif
#ifdef CS_OPT_STATS_TIME
    case CS_OPT_STATS_TIME:
#endif
#ifdef CS_OPT_STR_RTRUNC
    case CS_OPT_STR_RTRUNC:
#endif
#ifdef CS_OPT_TRUNCIGNORE
    case CS_OPT_TRUNCIGNORE:
#endif
	return OPTION_BOOL;
#ifdef CS_OPT_DATEFIRST
    case CS_OPT_DATEFIRST:
#endif
#ifdef CS_OPT_DATEFORMAT
    case CS_OPT_DATEFORMAT:
#endif
#ifdef CS_OPT_ISOLATION
    case CS_OPT_ISOLATION:
#endif
#ifdef CS_OPT_ROWCOUNT
    case CS_OPT_ROWCOUNT:
#endif
#ifdef CS_OPT_TEXTSIZE
    case CS_OPT_TEXTSIZE:
#endif
	return OPTION_INT;
#ifdef CS_OPT_AUTHOFF
    case CS_OPT_AUTHOFF:
#endif
#ifdef CS_OPT_AUTHON
    case CS_OPT_AUTHON:
#endif
#ifdef CS_OPT_CURREAD
    case CS_OPT_CURREAD:
#endif
#ifdef CS_OPT_CURWRITE
    case CS_OPT_CURWRITE:
#endif
#ifdef CS_OPT_IDENTITYOFF
    case CS_OPT_IDENTITYOFF:
#endif
#ifdef CS_OPT_IDENTITYON
    case CS_OPT_IDENTITYON:
#endif
	return OPTION_STRING;
    default:
	return OPTION_UNKNOWN;
    }
}

static char CS_CONNECTION_ct_options__doc__[] = 
"ct_options(CS_SET, option, value) -> status\n"
"ct_options(CS_GET, option) -> status, value\n"
#ifdef CS_CLEAR
"ct_options(CS_CLEAR, option) -> status\n"
#endif
;

static PyObject *CS_CONNECTION_ct_options(CS_CONNECTIONObj *self, PyObject *args)
{
    int action, option;
    PyObject *obj = NULL;
    CS_RETCODE status;
    CS_INT int_value;
    CS_BOOL bool_value;
    char *str_value;
    char str_buff[10240];
    CS_INT buff_len;

    if (!first_tuple_int(args, &action))
	return NULL;

    if (self->conn == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_CONNECTION has been dropped");
	return NULL;
    }

    switch (action) {
    case CS_SET:
	/* ct_options(CS_SET, option, value) -> status */
	if (!PyArg_ParseTuple(args, "iiO", &action, &option, &obj))
	    return NULL;

	switch (option_type(option)) {
	case OPTION_BOOL:
	    bool_value = PyInt_AsLong(obj);
	    if (PyErr_Occurred())
		return NULL;

	    /* PyErr_Clear(); */

	    SY_CONN_BEGIN_THREADS(self);
	    status = ct_options(self->conn, CS_SET, option,
				&bool_value, CS_UNUSED, NULL);
	    SY_CONN_END_THREADS(self);

	    if (self->debug)
		debug_msg("ct_options(conn%d, CS_SET, %s, %d, CS_UNUSED,"
			  " NULL) -> %s\n",
			  self->serial,
			  value_str(VAL_OPTION, option), (int)bool_value,
			  value_str(VAL_STATUS, status));
	    if (PyErr_Occurred())
		return NULL;

	    return PyInt_FromLong(status);

	case OPTION_INT:
	    int_value = PyInt_AsLong(obj);
	    if (PyErr_Occurred())
		return NULL;

	    /* PyErr_Clear(); */

	    SY_CONN_BEGIN_THREADS(self);
	    status = ct_options(self->conn, CS_SET, option,
				&int_value, CS_UNUSED, NULL);
	    SY_CONN_END_THREADS(self);

	    if (self->debug)
		debug_msg("ct_options(conn%d, CS_SET, %s, %d, CS_UNUSED,"
			  " NULL) -> %s\n",
			  self->serial,
			  value_str(VAL_OPTION, option), (int)int_value,
			  value_str(VAL_STATUS, status));
	    if (PyErr_Occurred())
		return NULL;

	    return PyInt_FromLong(status);

	case OPTION_STRING:
	    str_value = PyString_AsString(obj);
	    if (PyErr_Occurred())
		return NULL;

	    /* PyErr_Clear(); */

	    SY_CONN_BEGIN_THREADS(self);
	    status = ct_options(self->conn, CS_SET, option,
				str_value, CS_NULLTERM, NULL);
	    SY_CONN_END_THREADS(self);

	    if (self->debug)
		debug_msg("ct_options(conn%d, CS_SET, %s, \"%s\", CS_NULLTERM,"
			  " NULL) -> %s\n",
			  self->serial,
			  value_str(VAL_OPTION, option), str_value,
			  value_str(VAL_STATUS, status));
	    if (PyErr_Occurred())
		return NULL;

	    return PyInt_FromLong(status);

	default:
	    PyErr_SetString(PyExc_TypeError, "unhandled option value");
	    return NULL;
	}
	break;

    case CS_GET:
	/* ct_options(CS_GET, option) -> status, value */
	if (!PyArg_ParseTuple(args, "ii", &action, &option))
	    return NULL;

	switch (option_type(option)) {
	case OPTION_BOOL:
	    /* PyErr_Clear(); */

	    SY_CONN_BEGIN_THREADS(self);
	    status = ct_options(self->conn, CS_GET, option,
				&bool_value, CS_UNUSED, NULL);
	    SY_CONN_END_THREADS(self);

	    if (self->debug)
		debug_msg("ct_options(conn%d, CS_GET, %s, &value, CS_UNUSED,"
			  " NULL) -> %s, %d\n",
			  self->serial, value_str(VAL_OPTION, option),
			  value_str(VAL_STATUS, status), (int)bool_value);
	    if (PyErr_Occurred())
		return NULL;

	    return Py_BuildValue("ii", status, bool_value);

	case OPTION_INT:
	    /* PyErr_Clear(); */

	    SY_CONN_BEGIN_THREADS(self);
	    status = ct_options(self->conn, CS_GET, option,
				&int_value, CS_UNUSED, NULL);
	    SY_CONN_END_THREADS(self);

	    if (self->debug)
		debug_msg("ct_options(conn%d, CS_GET, %s, &value, CS_UNUSED,"
			  " NULL) -> %s, %d\n",
			  self->serial, value_str(VAL_OPTION, option),
			  value_str(VAL_STATUS, status), (int)int_value);
	    if (PyErr_Occurred())
		return NULL;

	    return Py_BuildValue("ii", status, int_value);

	case OPTION_STRING:
	    /* PyErr_Clear(); */

	    SY_CONN_BEGIN_THREADS(self);
	    status = ct_options(self->conn, CS_GET, option,
				str_buff, sizeof(str_buff), &buff_len);
	    SY_CONN_END_THREADS(self);

	    if (buff_len > sizeof(str_buff))
		buff_len = sizeof(str_buff);
	    if (self->debug)
		debug_msg("ct_options(conn%d, CS_GET, %s, buff, %d, &outlen)"
			  " -> %s, '%.*s'\n",
			  self->serial,
			  value_str(VAL_OPTION, option), sizeof(str_buff),
			  value_str(VAL_STATUS, status), (int)buff_len, str_buff);
	    if (PyErr_Occurred())
		return NULL;

	    return Py_BuildValue("is", status, str_buff);

	case OPTION_UNKNOWN:
	    PyErr_SetString(PyExc_TypeError, "unknown option value");
	    return NULL;

	default:
	    PyErr_SetString(PyExc_TypeError, "unhandled option value");
	    return NULL;
	}
	break;

#ifdef CS_CLEAR
    case CS_CLEAR:
	/* ct_options(CS_CLEAR, property) -> status */
	if (!PyArg_ParseTuple(args, "ii", &action, &option))
	    return NULL;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self);
	status = ct_options(self->conn, CS_CLEAR, option,
			    NULL, CS_UNUSED, NULL);
	SY_CONN_END_THREADS(self);

	if (self->debug)
	    debug_msg("ct_options(conn%d, CS_CLEAR, %s, NULL, CS_UNUSED,"
		      " NULL) -> %s\n",
		      self->serial, value_str(VAL_OPTION, option),
		      value_str(VAL_STATUS, status));
	if (PyErr_Occurred())
	    return NULL;

	return PyInt_FromLong(status);
#endif

    default:
	PyErr_SetString(PyExc_TypeError, "unknown action");
	return NULL;
    }
}

static struct PyMethodDef CS_CONNECTION_methods[] = {
    { "ct_diag", (PyCFunction)CS_CONNECTION_ct_diag, METH_VARARGS, CS_CONNECTION_ct_diag__doc__ },
    { "ct_cancel", (PyCFunction)CS_CONNECTION_ct_cancel, METH_VARARGS, CS_CONNECTION_ct_cancel__doc__ },
    { "ct_connect", (PyCFunction)CS_CONNECTION_ct_connect, METH_VARARGS, CS_CONNECTION_ct_connect__doc__ },
    { "ct_cmd_alloc", (PyCFunction)CS_CONNECTION_ct_cmd_alloc, METH_VARARGS, CS_CONNECTION_ct_cmd_alloc__doc__ },
#ifdef WANT_BULKCOPY
    { "blk_alloc", (PyCFunction)CS_CONNECTION_blk_alloc, METH_VARARGS, CS_CONNECTION_blk_alloc__doc__ },
#endif
    { "ct_close", (PyCFunction)CS_CONNECTION_ct_close, METH_VARARGS, CS_CONNECTION_ct_close__doc__ },
    { "ct_con_drop", (PyCFunction)CS_CONNECTION_ct_con_drop, METH_VARARGS, CS_CONNECTION_ct_con_drop__doc__ },
    { "ct_con_props", (PyCFunction)CS_CONNECTION_ct_con_props, METH_VARARGS, CS_CONNECTION_ct_con_props__doc__ },
    { "ct_options", (PyCFunction)CS_CONNECTION_ct_options, METH_VARARGS, CS_CONNECTION_ct_options__doc__ },
    { NULL }			/* sentinel */
};

static int conn_serial;

PyObject *conn_alloc(CS_CONTEXTObj *ctx, int enable_lock)
{
    CS_CONNECTIONObj *self;
    CS_RETCODE status;
    CS_CONNECTION *conn;

    self = PyObject_NEW(CS_CONNECTIONObj, &CS_CONNECTIONType);
    if (self == NULL)
	return NULL;

    SY_LEAK_REG(self);
    self->conn = NULL;
    self->ctx = NULL;
    self->strip = 0;
    self->debug = ctx->debug;
    self->serial = conn_serial++;
    if (enable_lock) {
	SY_LOCK_ALLOC(self);
    } else {
	SY_LOCK_CLEAR(self);
    }
    SY_THREAD_INIT(self);

    /* PyErr_Clear(); */

    SY_CTX_BEGIN_THREADS(ctx);
    status = ct_con_alloc(ctx->ctx, &conn);
    SY_CTX_END_THREADS(ctx);

    if (self->debug)
	debug_msg("ct_con_alloc(ctx%d, &conn) -> %s",
		  ctx->serial, value_str(VAL_STATUS, status));
    if (PyErr_Occurred()) {
	if (self->debug)
	    debug_msg("\n");
	Py_DECREF(self);
	return NULL;
    }

    if (status != CS_SUCCEED) {
	if (self->debug)
	    debug_msg(", None\n");
	Py_DECREF(self);
	return Py_BuildValue("iO", status, Py_None);
    }

    self->conn = conn;
    self->ctx = ctx;
    Py_INCREF(self->ctx);
    conn_add_object(self);
    if (self->debug)
	debug_msg(", conn%d\n", self->serial);
    return Py_BuildValue("iN", CS_SUCCEED, self);
}

static void CS_CONNECTION_dealloc(CS_CONNECTIONObj *self)
{
    SY_LEAK_UNREG(self);
    if (self->conn) {
	/* should check return == CS_SUCCEED, but we can't handle failure
	   here */
	CS_RETCODE status;

	status = ct_con_drop(self->conn);
	if (self->debug)
	    debug_msg("ct_con_drop(conn%d) -> %s\n",
		      self->serial, value_str(VAL_STATUS, status));
    }
    SY_LOCK_FREE(self);
    Py_XDECREF(self->ctx);
    conn_del_object(self);
    PyObject_DEL(self);
}

#define OFF(x) offsetof(CS_CONNECTIONObj, x)

static struct memberlist CS_CONNECTION_memberlist[] = {
    { "ctx", T_OBJECT, OFF(ctx), RO },
    { "strip", T_INT, OFF(strip) },
    { "debug", T_INT, OFF(debug) },
    { NULL }			/* Sentinel */
};

static PyObject *CS_CONNECTION_getattr(CS_CONNECTIONObj *self, char *name)
{
    PyObject *rv;

    rv = PyMember_Get((char *)self, CS_CONNECTION_memberlist, name);
    if (rv)
	return rv;
    PyErr_Clear();
    return Py_FindMethod(CS_CONNECTION_methods, (PyObject *)self, name);
}

static int CS_CONNECTION_setattr(CS_CONNECTIONObj *self, char *name, PyObject *v)
{
    if (v == NULL) {
	PyErr_SetString(PyExc_AttributeError, "Cannot delete attribute");
	return -1;
    }
    return PyMember_Set((char *)self, CS_CONNECTION_memberlist, name, v);
}

static char CS_CONNECTIONType__doc__[] = 
"Wrap the Sybase CS_CONNECTION structure and associated functionality.";

PyTypeObject CS_CONNECTIONType = {
    PyObject_HEAD_INIT(0)
    0,				/*ob_size*/
    "ConnectionType",		/*tp_name*/
    sizeof(CS_CONNECTIONObj),	/*tp_basicsize*/
    0,				/*tp_itemsize*/
    /* methods */
    (destructor)CS_CONNECTION_dealloc,/*tp_dealloc*/
    (printfunc)0,		/*tp_print*/
    (getattrfunc)CS_CONNECTION_getattr,	/*tp_getattr*/
    (setattrfunc)CS_CONNECTION_setattr,	/*tp_setattr*/
    (cmpfunc)0,			/*tp_compare*/
    (reprfunc)0,		/*tp_repr*/
    0,				/*tp_as_number*/
    0,				/*tp_as_sequence*/
    0,				/*tp_as_mapping*/
    (hashfunc)0,		/*tp_hash*/
    (ternaryfunc)0,		/*tp_call*/
    (reprfunc)0,		/*tp_str*/

    /* Space for future expansion */
    0L, 0L, 0L, 0L,
    CS_CONNECTIONType__doc__	/* Documentation string */
};
