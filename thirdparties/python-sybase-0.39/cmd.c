/******************************************************************

 Copyright 2001 by Object Craft P/L, Melbourne, Australia.

 LICENCE - see LICENCE file distributed with this software for details.

******************************************************************/

#include "sybasect.h"

static char CS_COMMAND_ct_bind__doc__[] = 
"ct_bind(int, datafmt) -> status, buf";

static PyObject *CS_COMMAND_ct_bind(CS_COMMANDObj *self, PyObject *args)
{
    CS_INT item;
    CS_DATAFMTObj *datafmt;
    DataBufObj *databuf;
    CS_RETCODE status;

    if (!PyArg_ParseTuple(args, "iO!", &item, &CS_DATAFMTType, &datafmt))
	return NULL;

    if (self->cmd == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_COMMAND has been dropped");
	return NULL;
    }

    databuf = (DataBufObj *)databuf_alloc((PyObject*)datafmt);
    if (databuf == NULL)
	return NULL;

    /* PyErr_Clear(); */

    SY_CONN_BEGIN_THREADS(self->conn);
    status = ct_bind(self->cmd, item, &databuf->fmt,
		     databuf->buff, databuf->copied, databuf->indicator);
    SY_CONN_END_THREADS(self->conn);

    if (self->debug) {
	debug_msg("ct_bind(cmd%d, %d, &datafmt%d->fmt=",
		  self->serial, (int)item, datafmt->serial);
	datafmt_debug(&databuf->fmt);
	debug_msg(", databuf%d->buff, databuf%d->copied, databuf%d->indicator)"
		  " -> %s",
		  databuf->serial, databuf->serial, databuf->serial,
		  value_str(VAL_STATUS, status));
    }
    if (PyErr_Occurred()) {
	if (self->debug)
	    debug_msg("\n");
	Py_DECREF(databuf);
        return NULL;
    }

    if (self->debug)
	debug_msg(", databuf%d\n", databuf->serial);
    return Py_BuildValue("iN", status, databuf);
}

static char CS_COMMAND_ct_cancel__doc__[] = 
"ct_cancel(type) -> status";

static PyObject *CS_COMMAND_ct_cancel(CS_COMMANDObj *self, PyObject *args)
{
    int type;
    CS_RETCODE status;

    if (!PyArg_ParseTuple(args, "i", &type))
	return NULL;

    if (self->cmd == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_COMMAND has been dropped");
	return NULL;
    }

    /* PyErr_Clear(); */

    SY_CONN_BEGIN_THREADS(self->conn);
    status = ct_cancel(NULL, self->cmd, type);
    SY_CONN_END_THREADS(self->conn);

    if (self->debug)
	debug_msg("ct_cancel(NULL, cmd%d, %s) -> %s\n",
		  self->serial,
		  value_str(VAL_CANCEL, type), value_str(VAL_STATUS, status));
    if (PyErr_Occurred())
        return NULL;

    return PyInt_FromLong(status);
}

static char CS_COMMAND_ct_cmd_drop__doc__[] = 
"ct_cmd_drop() -> status";

static PyObject *CS_COMMAND_ct_cmd_drop(CS_COMMANDObj *self, PyObject *args)
{
    CS_RETCODE status;

    if (!PyArg_ParseTuple(args, ""))
	return NULL;

    if (self->cmd == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_COMMAND has been dropped");
	return NULL;
    }

    /* PyErr_Clear(); */

    SY_CONN_BEGIN_THREADS(self->conn);
    status = ct_cmd_drop(self->cmd);
    SY_CONN_END_THREADS(self->conn);

    if (self->debug)
	debug_msg("ct_cmd_drop(cmd%d) -> %s\n",
		  self->serial, value_str(VAL_STATUS, status));
    if (status == CS_SUCCEED)
	self->cmd = NULL;
    if (PyErr_Occurred())
        return NULL;

    return PyInt_FromLong(status);
}

static char CS_COMMAND_ct_command__doc__[] = 
"ct_command(CS_LANG_CMD, sql [,option]) -> status\n"
"ct_command(CS_MSG_CMD, int) -> status\n"
"ct_command(CS_PACKAGE_CMD, name) -> status\n"
"ct_command(CS_RPC_CMD, name [,option]) -> status\n"
"ct_command(CS_SEND_DATA_CMD) -> status";

static PyObject *CS_COMMAND_ct_command(CS_COMMANDObj *self, PyObject *args)
{
    int type;
    char *databuf;
    CS_INT option = CS_UNUSED;
    CS_RETCODE status;
    char *type_str = NULL;

    if (!first_tuple_int(args, &type))
	return NULL;

    if (self->cmd == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_COMMAND has been dropped");
	return NULL;
    }

    switch (type) {
    case CS_LANG_CMD:
	/* ct_command(CS_LANG_CMD, sql [,option]) -> status */
	type_str = "CS_LANG_CMD";
    case CS_RPC_CMD:
	/* ct_command(CS_RPC_CMD, name [,option]) -> status */
	if (type_str == NULL)
	    type_str = "CS_RPC_CMD";
	if (!PyArg_ParseTuple(args, "is|i", &type, &databuf, &option))
	    return NULL;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_command(self->cmd, type, databuf, CS_NULLTERM, option);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug)
	    debug_msg("ct_command(cmd%d, %s, \"%s\", CS_NULLTERM, %s) -> %s\n",
		      self->serial, type_str, databuf,
		      value_str(VAL_OPTION, option),
		      value_str(VAL_STATUS, status));
	if (PyErr_Occurred())
	    return NULL;

	return PyInt_FromLong(status);

#ifdef CS_MSG_CMD
    case CS_MSG_CMD:
	/* ct_command(CS_MSG_CMD, int) -> status */
    {
	CS_INT num;

	if (!PyArg_ParseTuple(args, "ii", &type, &num))
	    return NULL;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_command(self->cmd, type, (CS_VOID*)&num, CS_UNUSED, CS_UNUSED);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug)
	    debug_msg("ct_command(cmd%d, CS_MSG_CMD, %d, CS_UNUSED, CS_UNUSED)"
		      " -> %s\n",
		      self->serial, (int)num, value_str(VAL_STATUS, status));
	if (PyErr_Occurred())
	    return NULL;

	return PyInt_FromLong(status);
    }
#endif

#ifdef CS_PACKAGE_CMD
    case CS_PACKAGE_CMD:
	/* ct_command(CS_PACKAGE_CMD, name) -> status */
	if (!PyArg_ParseTuple(args, "is", &type, &databuf))
	    return NULL;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_command(self->cmd, type, databuf, CS_NULLTERM, CS_UNUSED);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug)
	    debug_msg("ct_command(cmd%d, CS_PACKAGE_CMD, \"%s\", CS_NULLTERM,"
		      " CS_UNUSED) -> %s\n",
		      self->serial,
		      databuf, value_str(VAL_STATUS, status));
	if (PyErr_Occurred())
	    return NULL;

	return PyInt_FromLong(status);
#endif

    case CS_SEND_DATA_CMD:
	/* ct_command(CS_SEND_DATA_CMD) -> status */
	if (!PyArg_ParseTuple(args, "i", &type))
	    return NULL;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_command(self->cmd, type, NULL, CS_UNUSED, CS_COLUMN_DATA);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug)
	    debug_msg("ct_command(cmd%d, CS_SEND_DATA_CMD, NULL, CS_UNUSED,"
		      " CS_COLUMN_DATA) -> %s\n",
		      self->serial,
		      value_str(VAL_STATUS, status));
	if (PyErr_Occurred())
	    return NULL;

	return PyInt_FromLong(status);

    default:
	PyErr_SetString(PyExc_TypeError, "unknown type");
	return NULL;
    }
}

#ifdef HAVE_CT_CURSOR
static char CS_COMMAND_ct_cursor__doc__[] = 
"ct_cursor(CS_CURSOR_DECLARE, cursor_id, sql [,options]) -> status\n"
"ct_cursor(CS_CURSOR_UPDATE, table, sql [,options]) -> status\n"
"ct_cursor(CS_CURSOR_OPTION [,options]) -> status\n"
"ct_cursor(CS_CURSOR_ROWS, int) -> status\n"
"ct_cursor(CS_CURSOR_OPEN [,options]) -> status\n"
"ct_cursor(CS_CURSOR_DELETE, table) -> status\n"
"ct_cursor(CS_CURSOR_CLOSE [,options]) -> status\n"
"ct_cursor(CS_CURSOR_DEALLOC) -> status\n";

static PyObject *CS_COMMAND_ct_cursor(CS_COMMANDObj *self, PyObject *args)
{
    int type;
    char *name, *text;
    CS_INT option = CS_UNUSED;
    CS_RETCODE status;
    char *type_str = NULL;

    if (!first_tuple_int(args, &type))
	return NULL;

    if (self->cmd == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_COMMAND has been dropped");
	return NULL;
    }

    switch (type) {
    case CS_CURSOR_DECLARE:
	/* ct_cursor(CS_CURSOR_DECLARE, cursor_id, sql [,options]) -> status */
	type_str = "CS_CURSOR_DECLARE";
    case CS_CURSOR_UPDATE:
	/* ct_cursor(CS_CURSOR_UPDATE, table, sql [,options]) -> status */
	if (type_str == NULL)
	    type_str = "CS_CURSOR_UPDATE";
	if (!PyArg_ParseTuple(args, "iss|i", &type, &name, &text, &option))
	    return NULL;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_cursor(self->cmd, type,
			   name, CS_NULLTERM, text, CS_NULLTERM, option);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug)
	    debug_msg("ct_cursor(cmd%d, %s, \"%s\", CS_NULLTERM, \"%s\","
		      " CS_NULLTERM, %s) -> %s\n",
		      self->serial, type_str, name, text,
		      value_str(VAL_CURSOROPT, option),
		      value_str(VAL_STATUS, status));
	if (PyErr_Occurred())
	    return NULL;

	return PyInt_FromLong(status);

    case CS_CURSOR_OPTION:
	/* ct_cursor(CS_CURSOR_OPTION [,options]) -> status */
	type_str = "CS_CURSOR_OPTION";
    case CS_CURSOR_OPEN:
	/* ct_cursor(CS_CURSOR_OPEN [,options]) -> status */
	if (type_str == NULL)
	    type_str = "CS_CURSOR_OPEN";
    case CS_CURSOR_CLOSE:
	/* ct_cursor(CS_CURSOR_CLOSE [,options]) -> status */
	if (type_str == NULL)
	    type_str = "CS_CURSOR_CLOSE";
	if (!PyArg_ParseTuple(args, "i|i", &type, &option))
	    return NULL;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_cursor(self->cmd, type,
			   NULL, CS_UNUSED, NULL, CS_UNUSED, option);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug)
	    debug_msg("ct_cursor(cmd%d, %s, NULL, CS_UNUSED, NULL, CS_UNUSED,"
		      " %s) -> %s\n",
		      self->serial, type_str,
		      value_str(VAL_CURSOROPT, option),
		      value_str(VAL_STATUS, status));
	if (PyErr_Occurred())
	    return NULL;

	return PyInt_FromLong(status);

    case CS_CURSOR_ROWS:
	/* ct_cursor(CS_CURSOR_ROWS, int) -> status */
	if (!PyArg_ParseTuple(args, "ii", &type, &option))
	    return NULL;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_cursor(self->cmd, type,
			   NULL, CS_UNUSED, NULL, CS_UNUSED, option);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug)
	    debug_msg("ct_cursor(cmd%d, CS_CURSOR_ROWS, NULL, CS_UNUSED,"
		      " NULL, CS_UNUSED, %s) -> %s\n",
		      self->serial,
		      value_str(VAL_CURSOROPT, option),
		      value_str(VAL_STATUS, status));
	if (PyErr_Occurred())
	    return NULL;

	return PyInt_FromLong(status);

    case CS_CURSOR_DELETE:
	/* ct_cursor(CS_CURSOR_DELETE, table) -> status */
	if (!PyArg_ParseTuple(args, "is", &type, &name))
	    return NULL;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_cursor(self->cmd, type,
			   name, CS_NULLTERM, NULL, CS_UNUSED, CS_UNUSED);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug)
	    debug_msg("ct_cursor(cmd%d, CS_CURSOR_DELETE, \"%s\", CS_NULLTERM,"
		      " NULL, CS_UNUSED, CS_UNUSED) -> %s\n",
		      self->serial, name, value_str(VAL_STATUS, status));
	if (PyErr_Occurred())
	    return NULL;

	return PyInt_FromLong(status);

    case CS_CURSOR_DEALLOC:
	/* ct_cursor(CS_CURSOR_DEALLOC) -> status */
	if (!PyArg_ParseTuple(args, "i", &type))
	    return NULL;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_cursor(self->cmd, type,
			   NULL, CS_UNUSED, NULL, CS_UNUSED, CS_UNUSED);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug)
	    debug_msg("ct_cursor(cmd%d, CS_CURSOR_DEALLOC, NULL, CS_UNUSED,"
		      " NULL, CS_UNUSED, CS_UNUSED) -> %s\n",
		      self->serial, value_str(VAL_STATUS, status));
	if (PyErr_Occurred())
	    return NULL;

	return PyInt_FromLong(status);

    default:
	PyErr_SetString(PyExc_TypeError, "unknown type");
	return NULL;
    }
}
#endif

#ifdef HAVE_CT_DATA_INFO
static char CS_COMMAND_ct_data_info__doc__[] = 
"ct_data_info(CS_SET, iodesc) -> status\n"
"ct_data_info(CS_GET, num) -> status, iodesc";

static PyObject *CS_COMMAND_ct_data_info(CS_COMMANDObj *self, PyObject *args)
{
    int action;
    CS_INT num;
    CS_IODESC iodesc;
    CS_IODESCObj *desc;
    CS_RETCODE status;

    if (!first_tuple_int(args, &action))
	return NULL;

    if (self->cmd == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_COMMAND has been dropped");
	return NULL;
    }

    switch (action) {
    case CS_SET:
	/* ct_data_info(CS_SET, int, iodesc) -> status */
	if (!PyArg_ParseTuple(args, "iO!",
			      &action, &CS_IODESCType, &desc))
	    return NULL;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_data_info(self->cmd, CS_SET, CS_UNUSED, &desc->iodesc);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug)
	    debug_msg("ct_data_info(cmd%d, CS_SET, CS_UNUSED, iodesc%d)"
		      " -> %s\n",
		      self->serial, desc->serial,
		      value_str(VAL_STATUS, status));
	if (PyErr_Occurred())
	    return NULL;

	return PyInt_FromLong(status);

    case CS_GET:
	/* ct_data_info(CS_GET, int) -> status, iodesc */
	if (!PyArg_ParseTuple(args, "ii", &action, &num))
	    return NULL;
	memset(&iodesc, 0, sizeof(iodesc));

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_data_info(self->cmd, CS_GET, num, &iodesc);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug)
	    debug_msg("ct_data_info(cmd%d, CS_GET, %d, &iodesc) -> %s",
		      self->serial, (int)num, value_str(VAL_STATUS, status));
	if (PyErr_Occurred()) {
	    if (self->debug)
		debug_msg("\n");
	    return NULL;
	}

	if (status != CS_SUCCEED) {
	    if (self->debug)
		debug_msg(", None\n");
	    return Py_BuildValue("iO", status, Py_None);
	}
	desc = (CS_IODESCObj*)iodesc_alloc(&iodesc);
	if (desc == NULL) {
	    if (self->debug)
		debug_msg("\n");
	    return NULL;
	}

	if (self->debug)
	    debug_msg(", iodesc%d\n", desc->serial);
	return Py_BuildValue("iN", status, desc);

    default:
	PyErr_SetString(PyExc_TypeError, "unknown action");
	return NULL;
    }
}
#endif

static char CS_COMMAND_ct_describe__doc__[] = 
"ct_describe(int) -> status, datafmt";

static PyObject *CS_COMMAND_ct_describe(CS_COMMANDObj *self, PyObject *args)
{
    CS_INT num;
    CS_DATAFMT datafmt;
    PyObject *fmt;
    CS_RETCODE status;

    if (!PyArg_ParseTuple(args, "i", &num))
	return NULL;

    if (self->cmd == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_COMMAND has been dropped");
	return NULL;
    }

    memset(&datafmt, 0, sizeof(datafmt));

    /* PyErr_Clear(); */

    SY_CONN_BEGIN_THREADS(self->conn);
    status = ct_describe(self->cmd, num, &datafmt);
    SY_CONN_END_THREADS(self->conn);

    if (self->debug)
	debug_msg("ct_describe(cmd%d, %d, &fmt) -> %s",
		  self->serial, (int)num, value_str(VAL_STATUS, status));
    if (PyErr_Occurred()) {
	if (self->debug)
	    debug_msg("\n");
	return NULL;
    }

    if (status != CS_SUCCEED) {
	if (self->debug)
	    debug_msg(", None\n");
	return Py_BuildValue("iO", status, Py_None);
    }

    fmt = datafmt_alloc(&datafmt, self->strip);
    if (fmt == NULL) {
	if (self->debug)
	    debug_msg("\n");
	return NULL;
    }

    if (self->debug) {
	debug_msg(", datafmt%d=", ((CS_DATAFMTObj*)fmt)->serial);
	datafmt_debug(&datafmt);
	debug_msg("\n");
    }
    return Py_BuildValue("iN", status, fmt);
}

#ifdef HAVE_CT_DYNAMIC
static char CS_COMMAND_ct_dynamic__doc__[] = 
"ct_dynamic(CS_CURSOR_DECLARE, dyn_id, cursor_id) -> status\n"
"ct_dynamic(CS_DEALLOC, dyn_id) -> status\n"
"ct_dynamic(CS_DESCRIBE_INPUT, dyn_id) -> status\n"
"ct_dynamic(CS_DESCRIBE_OUTPUT, dyn_id) -> status\n"
"ct_dynamic(CS_EXECUTE, dyn_id) -> status\n"
"ct_dynamic(CS_EXEC_IMMEDIATE, sql) -> status\n"
"ct_dynamic(CS_PREPARE, dyn_id, sql) -> status";

static PyObject *CS_COMMAND_ct_dynamic(CS_COMMANDObj *self, PyObject *args)
{
    int type;
    char *id, *buff;
    char *cmd_str = NULL;
    CS_RETCODE status;

    if (!first_tuple_int(args, &type))
	return NULL;

    if (self->cmd == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_COMMAND has been dropped");
	return NULL;
    }

    switch (type) {
    case CS_CURSOR_DECLARE:
	/* ct_dynamic(CS_CURSOR_DECLARE, dyn_id, cursor_id) -> status */
	cmd_str = "CS_CURSOR_DECLARE";
    case CS_PREPARE:
	/* ct_dynamic(CS_PREPARE, dyn_id, sql) -> status */
	if (cmd_str == NULL)
	    cmd_str = "CS_PREPARE";
	if (!PyArg_ParseTuple(args, "iss", &type, &id, &buff))
	    return NULL;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_dynamic(self->cmd, type,
			    id, CS_NULLTERM, buff, CS_NULLTERM);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug)
	    debug_msg("ct_dynamic(cmd%d, %s, \"%s\", CS_NULLTERM, \"%s\","
		      " CS_NULLTERM) -> %s\n",
		      self->serial, cmd_str, id, buff,
		      value_str(VAL_STATUS, status));
	if (PyErr_Occurred())
	    return NULL;

	return PyInt_FromLong(status);

    case CS_DEALLOC:
	/* ct_dynamic(CS_DEALLOC, dyn_id) -> status */
	cmd_str = "CS_DEALLOC";
    case CS_DESCRIBE_INPUT:
	/* ct_dynamic(CS_DESCRIBE_INPUT, dyn_id) -> status */
	if (cmd_str == NULL)
	    cmd_str = "CS_DESCRIBE_INPUT";
    case CS_DESCRIBE_OUTPUT:
	/* ct_dynamic(CS_DESCRIBE_OUTPUT, dyn_id) -> status */
	if (cmd_str == NULL)
	    cmd_str = "CS_DESCRIBE_OUTPUT";
    case CS_EXECUTE:
	/* ct_dynamic(CS_EXECUTE, dyn_id) -> status */
	if (cmd_str == NULL)
	    cmd_str = "CS_EXECUTE";
	if (!PyArg_ParseTuple(args, "is", &type, &id))
	    return NULL;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_dynamic(self->cmd, type,
			    id, CS_NULLTERM, NULL, CS_UNUSED);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug)
	    debug_msg("ct_dynamic(cmd%d, %s, \"%s\", CS_NULLTERM, NULL,"
		      " CS_UNUSED) -> %s\n",
		      self->serial, cmd_str, id,
		      value_str(VAL_STATUS, status));
	if (PyErr_Occurred())
	    return NULL;

	return PyInt_FromLong(status);

    case CS_EXEC_IMMEDIATE:
	/* ct_dynamic(CS_EXEC_IMMEDIATE, sql) -> status */
	if (!PyArg_ParseTuple(args, "is", &type, &buff))
	    return NULL;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_dynamic(self->cmd, type,
			    NULL, CS_UNUSED, buff, CS_NULLTERM);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug)
	    debug_msg("ct_dynamic(cmd%d, CS_EXEC_IMMEDIATE, NULL, CS_UNUSED,"
		      " \"%s\", CS_NULLTERM) -> %s\n",
		      self->serial, buff, value_str(VAL_STATUS, status));
	if (PyErr_Occurred())
	    return NULL;

	return PyInt_FromLong(status);

    default:
	PyErr_SetString(PyExc_TypeError, "unknown dynamic command");
	return NULL;
    }
}
#endif

static char CS_COMMAND_ct_fetch__doc__[] = 
"ct_fetch() -> result, rows_read";

static PyObject *CS_COMMAND_ct_fetch(CS_COMMANDObj *self, PyObject *args)
{
    CS_RETCODE status;
    CS_INT rows_read = 0;

    if (!PyArg_ParseTuple(args, ""))
	return NULL;

    if (self->cmd == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_COMMAND has been dropped");
	return NULL;
    }

    /* PyErr_Clear(); */

    SY_CONN_BEGIN_THREADS(self->conn);
    status = ct_fetch(self->cmd, CS_UNUSED, CS_UNUSED, CS_UNUSED, &rows_read);
    SY_CONN_END_THREADS(self->conn);

    if (self->debug)
	debug_msg("ct_fetch(cmd%d, CS_UNUSED, CS_UNUSED, CS_UNUSED,"
		  " &rows_read) -> %s, %d\n",
		  self->serial, value_str(VAL_STATUS, status), (int)rows_read);
    if (PyErr_Occurred())
	return NULL;

    return Py_BuildValue("ii", status, rows_read);
}

static char CS_COMMAND_ct_get_data__doc__[] = 
"ct_get_data(num, databuf) -> result, len";

static PyObject *CS_COMMAND_ct_get_data(CS_COMMANDObj *self, PyObject *args)
{
    DataBufObj *databuf;
    int num;
    CS_RETCODE status;

    if (!PyArg_ParseTuple(args, "iO!", &num, &DataBufType, &databuf))
	return NULL;

    if (self->cmd == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_COMMAND has been dropped");
	return NULL;
    }

    /* PyErr_Clear(); */

    SY_CONN_BEGIN_THREADS(self->conn);
    status = ct_get_data(self->cmd, (CS_INT)num,
			 databuf->buff, databuf->fmt.maxlength,
			 &databuf->copied[0]);
    databuf->indicator[0] = 0;
    SY_CONN_END_THREADS(self->conn);

    if (self->debug)
	debug_msg("ct_get_data(cmd%d, %d, databuf%d->buff,"
		  " %d, &databuf%d->copied[0]) -> %s, %d\n",
		  self->serial, num, databuf->serial,
		  (int)databuf->fmt.maxlength, databuf->serial,
		  value_str(VAL_STATUS, status), (int)databuf->copied[0]);
    if (PyErr_Occurred())
	return NULL;

    return Py_BuildValue("ii", status, databuf->copied[0]);
}

static char CS_COMMAND_ct_param__doc__[] = 
"ct_param(param) -> status";

static PyObject *CS_COMMAND_ct_param(CS_COMMANDObj *self, PyObject *args)
{
    PyObject *obj;
    CS_RETCODE status;

    if (!PyArg_ParseTuple(args, "O", &obj))
	return NULL;

    if (self->cmd == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_COMMAND has been dropped");
	return NULL;
    }

    /* FIXME: Need to handle CS_UPDATECOL variant */
    if (DataBuf_Check(obj)) {
	DataBufObj *databuf = (DataBufObj *)obj;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_param(self->cmd, &databuf->fmt,
			  databuf->buff, databuf->copied[0],
			  databuf->indicator[0]);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug) {
	    debug_msg("ct_param(cmd%d, &databuf%d->fmt=",
		      self->serial, databuf->serial);
	    datafmt_debug(&databuf->fmt);
	    debug_msg(", databuf%d->buff, %d, %d) -> %s\n",
		      databuf->serial,
		      (int)databuf->copied[0], databuf->indicator[0],
		      value_str(VAL_STATUS, status));
	}
	if (PyErr_Occurred())
	    return NULL;
    } else if (CS_DATAFMT_Check(obj)) {
	CS_DATAFMTObj *datafmt = (CS_DATAFMTObj *)obj;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_param(self->cmd, &datafmt->fmt,
			  NULL, CS_UNUSED, (CS_SMALLINT)CS_UNUSED);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug) {
	    debug_msg("ct_param(cmd%d, &fmt=", self->serial);
	    datafmt_debug(&datafmt->fmt);
	    debug_msg(", NULL, CS_UNUSED, CS_UNUSED) -> %s\n",
		      value_str(VAL_STATUS, status));
	}
	if (PyErr_Occurred())
	    return NULL;
    } else {
	PyErr_SetString(PyExc_TypeError, "expect CS_DATAFMT or DataBuf");
	return NULL;
	
    }
    return PyInt_FromLong(status);
}

#ifdef CS_ORDERBY_COLS
static PyObject *build_int_list(CS_INT *values, int len)
{
    int i;			/* iterate over table columns */
    PyObject *list;		/* list containing all columns */

    list = PyList_New(len);
    if (list == NULL)
	return NULL;

    for (i = 0; i < len; i++) {
	PyObject *num;

	num = PyInt_FromLong(values[i]);
	if (num == NULL) {
	    Py_DECREF(list);
	    return NULL;
	}
	if (PyList_SetItem(list, i, num) != 0) {
	    Py_DECREF(list);
	    return NULL;
	}
    }

    return list;
}
#endif

static char CS_COMMAND_ct_res_info__doc__[] = 
"ct_res_info(CS_BROWSE_INFO) -> status, bool\n"
"ct_res_info(CS_CMD_NUMBER) -> status, int\n"
#ifdef CS_MSGTYPE
"ct_res_info(CS_MSGTYPE) -> status, int\n"
#endif
"ct_res_info(CS_NUM_COMPUTES) -> status, int\n"
"ct_res_info(CS_NUMDATA) -> status, int\n"
"ct_res_info(CS_NUMORDER_COLS) -> status, int\n"
#ifdef CS_ORDERBY_COLS
"ct_res_info(CS_ORDERBY_COLS) -> status, list of int\n"
#endif
"ct_res_info(CS_ROW_COUNT) -> status, int\n"
"ct_res_info(CS_TRANS_STATE) -> status, int";

static PyObject *CS_COMMAND_ct_res_info(CS_COMMANDObj *self, PyObject *args)
{
    int type;
    CS_RETCODE status;
    CS_INT int_val;
    CS_BOOL bool_val;
    char *type_str = NULL;

    if (!PyArg_ParseTuple(args, "i", &type))
	return NULL;

    if (self->cmd == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_COMMAND has been dropped");
	return NULL;
    }

    switch (type) {
    case CS_BROWSE_INFO:
	/* ct_res_info(CS_BROWSE_INFO) -> status, bool */
	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_res_info(self->cmd, type, &bool_val, CS_UNUSED, NULL);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug)
	    debug_msg("ct_res_info(cmd%d, CS_BROWSE_INFO, &value, CS_UNUSED,"
		      " NULL) -> %s, %d\n",
		      self->serial,
		      value_str(VAL_STATUS, status), (int)bool_val);
	if (PyErr_Occurred())
	    return NULL;

	return Py_BuildValue("ii", status, bool_val);

#ifdef CS_MSGTYPE
    case CS_MSGTYPE:
	/* ct_res_info(CS_MSGTYPE) -> status, int */
    {
	CS_USHORT ushort_val;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_res_info(self->cmd, type, &ushort_val, CS_UNUSED, NULL);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug)
	    debug_msg("ct_res_info(cmd%d, CS_MSGTYPE, &value, CS_UNUSED, NULL)"
		      " -> %s, %d\n",
		      self->serial, value_str(VAL_STATUS, status), ushort_val);
	if (PyErr_Occurred())
	    return NULL;

	return Py_BuildValue("ii", status, ushort_val);
    }
#endif

    case CS_CMD_NUMBER:
	/* ct_res_info(CS_CMD_NUMBER) -> status, int */
	type_str = "CS_CMD_NUMBER";
    case CS_NUM_COMPUTES:
	/* ct_res_info(CS_NUM_COMPUTES) -> status, int */
	if (type_str == NULL)
	    type_str = "CS_NUM_COMPUTES";
    case CS_NUMDATA:
	/* ct_res_info(CS_NUMDATA) -> status, int */
	if (type_str == NULL)
	    type_str = "CS_NUMDATA";
    case CS_NUMORDERCOLS:
	/* ct_res_info(CS_NUMORDER_COLS) -> status, int */
	if (type_str == NULL)
	    type_str = "CS_NUMORDER_COLS";
    case CS_ROW_COUNT:
	/* ct_res_info(CS_ROW_COUNT) -> status, int */
	if (type_str == NULL)
	    type_str = "CS_ROW_COUNT";
    case CS_TRANS_STATE:
	/* ct_res_info(CS_TRANS_STATE) -> status, int */
	if (type_str == NULL)
	    type_str = "CS_TRANS_STATE";
	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_res_info(self->cmd, type, &int_val, CS_UNUSED, NULL);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug)
	    debug_msg("ct_res_info(cmd%d, %s, &value, CS_UNUSED, NULL)"
		      " -> %s, %d\n",
		      self->serial, type_str,
		      value_str(VAL_STATUS, status), (int)int_val);
	if (PyErr_Occurred())
	    return NULL;

	return Py_BuildValue("ii", status, int_val);

#ifdef CS_ORDERBY_COLS
    case CS_ORDERBY_COLS:
	/* ct_res_info(CS_ORDERBY_COLS) -> status, list of int */
    {
	PyObject *list;
	CS_INT *col_nums;

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_res_info(self->cmd, CS_NUMORDERCOLS, &int_val, CS_UNUSED, NULL);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug)
	    debug_msg("ct_res_info(cmd%d, CS_NUMORDERCOLS, &value, CS_UNUSED,"
		      " NULL) -> %s, %d\n",
		      self->serial,
		      value_str(VAL_STATUS, status), (int)int_val);
	if (PyErr_Occurred())
	    return NULL;

	if (status != CS_SUCCEED)
	    return Py_BuildValue("iO", status, Py_None);

	if (int_val <= 0)
	    return Py_BuildValue("i[]", status);

	col_nums = malloc(sizeof(*col_nums) * int_val);
	if (col_nums == NULL)
	    return PyErr_NoMemory();

	/* PyErr_Clear(); */

	SY_CONN_BEGIN_THREADS(self->conn);
	status = ct_res_info(self->cmd, CS_ORDERBY_COLS,
			     col_nums, sizeof(*col_nums) * int_val, NULL);
	SY_CONN_END_THREADS(self->conn);

	if (self->debug) {
	    int i;

	    debug_msg("ct_res_info(cmd%d, CS_ORDERBY_COLS, &col_nums, %d,"
		      " NULL) -> %s, [",
		      self->serial, (int)(sizeof(*col_nums) * int_val),
		      value_str(VAL_STATUS, status));
	    for (i = 0; i < int_val; i++) {
		if (i > 0)
		    debug_msg(",");
		debug_msg("%d", (int)col_nums[i]);
	    }
	    debug_msg("]\n");
	}
	if (PyErr_Occurred()) {
	    free(col_nums);
	    return NULL;
	}

	list = build_int_list(col_nums, int_val);
	free(col_nums);
	if (list == NULL)
	    return NULL;
	return Py_BuildValue("iN", status, list);
    }
#endif

    default:
	PyErr_SetString(PyExc_TypeError, "unknown command");
	return NULL;
    }
}

static char CS_COMMAND_ct_results__doc__[] = 
"ct_results() -> status, result";

static PyObject *CS_COMMAND_ct_results(CS_COMMANDObj *self, PyObject *args)
{
    CS_RETCODE status;
    CS_INT result = 0;

    if (!PyArg_ParseTuple(args, ""))
	return NULL;

    if (self->cmd == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_COMMAND has been dropped");
	return NULL;
    }

    /* PyErr_Clear(); */

    if (self->debug)
        debug_msg("::ct_results(cmd%d): using cmd \"%s\"\n", self->serial, self->cmd);
    SY_CONN_BEGIN_THREADS(self->conn);
    status = ct_results(self->cmd, &result);
    SY_CONN_END_THREADS(self->conn);

    if (self->debug)
	debug_msg("ct_results(cmd%d, &result) -> %s, %s\n",
		  self->serial, value_str(VAL_STATUS, status),
		  value_str(VAL_RESULT, result));
    if (PyErr_Occurred())
	return NULL;

    return Py_BuildValue("ii", status, result);
}

static char CS_COMMAND_ct_send__doc__[] = 
"ct_send() -> status";

static PyObject *CS_COMMAND_ct_send(CS_COMMANDObj *self, PyObject *args)
{
    CS_RETCODE status;

    if (!PyArg_ParseTuple(args, ""))
	return NULL;

    if (self->cmd == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_COMMAND has been dropped");
	return NULL;
    }

    /* PyErr_Clear(); */

    SY_CONN_BEGIN_THREADS(self->conn);
    status = ct_send(self->cmd);
    SY_CONN_END_THREADS(self->conn);

    if (self->debug)
	debug_msg("ct_send(cmd%d) -> %s\n",
		  self->serial, value_str(VAL_STATUS, status));
    if (PyErr_Occurred())
	return NULL;

    return PyInt_FromLong(status);
}

#ifdef HAVE_CT_SEND_DATA
static char CS_COMMAND_ct_send_data__doc__[] = 
"ct_send_data(databuf) -> status";

static PyObject *CS_COMMAND_ct_send_data(CS_COMMANDObj *self, PyObject *args)
{
    CS_RETCODE status;
    DataBufObj *databuf;

    if (!PyArg_ParseTuple(args, "O!", &DataBufType, &databuf))
	return NULL;

    if (self->cmd == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_COMMAND has been dropped");
	return NULL;
    }

    /* PyErr_Clear(); */

    SY_CONN_BEGIN_THREADS(self->conn);
    status = ct_send_data(self->cmd, databuf->buff, databuf->copied[0]);
    SY_CONN_END_THREADS(self->conn);

    if (self->debug)
	debug_msg("ct_send_data(cmd%d, databuf%d->buff, %d) -> %s\n",
		  self->serial, databuf->serial, (int)databuf->copied[0],
		  value_str(VAL_STATUS, status));
    if (PyErr_Occurred())
	return NULL;

    return PyInt_FromLong(status);
}
#endif

#ifdef HAVE_CT_SETPARAM
static char CS_COMMAND_ct_setparam__doc__[] = 
"ct_setparam(databuf) -> status";

static PyObject *CS_COMMAND_ct_setparam(CS_COMMANDObj *self, PyObject *args)
{
    DataBufObj *databuf;
    CS_RETCODE status;

    if (!PyArg_ParseTuple(args, "O!", &DataBufType, &databuf))
	return NULL;

    if (self->cmd == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_COMMAND has been dropped");
	return NULL;
    }

    /* PyErr_Clear(); */

    SY_CONN_BEGIN_THREADS(self->conn);
    status = ct_setparam(self->cmd, &databuf->fmt,
			 databuf->buff, &databuf->copied[0],
			 &databuf->indicator[0]);
    SY_CONN_END_THREADS(self->conn);

    if (self->debug) {
	debug_msg("ct_setparam(cmd%d, &databuf%d->fmt=",
		  self->serial, databuf->serial);
	datafmt_debug(&databuf->fmt);
	debug_msg(", databuf%d->buff,"
		  " &databuf%d->copied[0], &databuf%d->indicator[0]) -> %s\n",
		  databuf->serial, databuf->serial, databuf->serial,
		  value_str(VAL_STATUS, status));
    }
    if (PyErr_Occurred())
	return NULL;

    return PyInt_FromLong(status);
}
#endif

static struct PyMethodDef CS_COMMAND_methods[] = {
    { "ct_bind", (PyCFunction)CS_COMMAND_ct_bind, METH_VARARGS, CS_COMMAND_ct_bind__doc__ },
    { "ct_cancel", (PyCFunction)CS_COMMAND_ct_cancel, METH_VARARGS, CS_COMMAND_ct_cancel__doc__ },
    { "ct_command", (PyCFunction)CS_COMMAND_ct_command, METH_VARARGS, CS_COMMAND_ct_command__doc__ },
    { "ct_cmd_drop", (PyCFunction)CS_COMMAND_ct_cmd_drop, METH_VARARGS, CS_COMMAND_ct_cmd_drop__doc__ },
#ifdef HAVE_CT_CURSOR
    { "ct_cursor", (PyCFunction)CS_COMMAND_ct_cursor, METH_VARARGS, CS_COMMAND_ct_cursor__doc__ },
#endif
#ifdef HAVE_CT_DATA_INFO
    { "ct_data_info", (PyCFunction)CS_COMMAND_ct_data_info, METH_VARARGS, CS_COMMAND_ct_data_info__doc__ },
#endif
    { "ct_describe", (PyCFunction)CS_COMMAND_ct_describe, METH_VARARGS, CS_COMMAND_ct_describe__doc__ },
#ifdef HAVE_CT_DYNAMIC
    { "ct_dynamic", (PyCFunction)CS_COMMAND_ct_dynamic, METH_VARARGS, CS_COMMAND_ct_dynamic__doc__ },
#endif
    { "ct_fetch", (PyCFunction)CS_COMMAND_ct_fetch, METH_VARARGS, CS_COMMAND_ct_fetch__doc__ },
    { "ct_get_data", (PyCFunction)CS_COMMAND_ct_get_data, METH_VARARGS, CS_COMMAND_ct_get_data__doc__ },
    { "ct_param", (PyCFunction)CS_COMMAND_ct_param, METH_VARARGS, CS_COMMAND_ct_param__doc__ },
    { "ct_res_info", (PyCFunction)CS_COMMAND_ct_res_info, METH_VARARGS, CS_COMMAND_ct_res_info__doc__ },
    { "ct_results", (PyCFunction)CS_COMMAND_ct_results, METH_VARARGS, CS_COMMAND_ct_results__doc__ },
    { "ct_send", (PyCFunction)CS_COMMAND_ct_send, METH_VARARGS, CS_COMMAND_ct_send__doc__ },
#ifdef HAVE_CT_SEND_DATA
    { "ct_send_data", (PyCFunction)CS_COMMAND_ct_send_data, METH_VARARGS, CS_COMMAND_ct_send_data__doc__ },
#endif
#ifdef HAVE_CT_SETPARAM
    { "ct_setparam", (PyCFunction)CS_COMMAND_ct_setparam, METH_VARARGS, CS_COMMAND_ct_setparam__doc__ },
#endif
    { NULL }			/* sentinel */
};

static int cmd_serial;

PyObject *cmd_alloc(CS_CONNECTIONObj *conn)
{
    CS_COMMANDObj *self;
    CS_RETCODE status;
    CS_COMMAND *cmd;

    self = PyObject_NEW(CS_COMMANDObj, &CS_COMMANDType);
    if (self == NULL)
	return NULL;
    SY_LEAK_REG(self);
    self->is_eed = 0;
    self->cmd = NULL;
    self->conn = NULL;
    self->strip = conn->strip;
    self->debug = conn->debug;
    self->serial = cmd_serial++;

    /* PyErr_Clear(); */

    SY_CONN_BEGIN_THREADS(conn);
    status = ct_cmd_alloc(conn->conn, &cmd);
    SY_CONN_END_THREADS(conn);

    if (self->debug)
	debug_msg("ct_cmd_alloc(conn%d, &cmd) -> %s",
		  conn->serial, value_str(VAL_STATUS, status));
    if (PyErr_Occurred()) {
	if (self->debug)
	    debug_msg("\n");
	Py_DECREF(self);
	return NULL;
    }

    if (status != CS_SUCCEED) {
	Py_DECREF(self);
	if (self->debug)
	    debug_msg(", None\n");
	return Py_BuildValue("iO", status, Py_None);
    }

    self->cmd = cmd;
    self->conn = conn;
    Py_INCREF(self->conn);
    if (self->debug)
	debug_msg(", cmd%d\n", self->serial);
    return Py_BuildValue("iN", CS_SUCCEED, self);
}

PyObject *cmd_eed(CS_CONNECTIONObj *conn, CS_COMMAND *eed)
{
    CS_COMMANDObj *self;

    self = PyObject_NEW(CS_COMMANDObj, &CS_COMMANDType);
    if (self == NULL)
	return NULL;

    SY_LEAK_REG(self);
    self->is_eed = 1;
    self->cmd = eed;
    self->conn = conn;
    Py_INCREF(self->conn);

    self->strip = 0;
    self->debug = conn->debug;
    self->serial = cmd_serial++;

    return (PyObject*)self;
}

static void CS_COMMAND_dealloc(CS_COMMANDObj *self)
{
    SY_LEAK_UNREG(self);
    if (!self->is_eed && self->cmd) {
	/* should check return == CS_SUCCEED, but we can't handle failure
	   here */
	CS_RETCODE status;

	status = ct_cmd_drop(self->cmd);
	if (self->debug)
	    debug_msg("ct_cmd_drop(cmd%d) -> %s\n",
		      self->serial, value_str(VAL_STATUS, status));
    }
    Py_XDECREF(self->conn);
    PyObject_DEL(self);
}

#define OFFSET(x) offsetof(CS_COMMANDObj, x)

static struct memberlist CS_COMMAND_memberlist[] = {
    { "is_eed", T_INT,    OFFSET(is_eed), RO },
    { "conn",   T_OBJECT, OFFSET(conn),   RO },
    { "strip",  T_INT,    OFFSET(strip) },
    { "debug",  T_INT,    OFFSET(debug) },
    { NULL }			/* Sentinel */
};

static PyObject *CS_COMMAND_getattr(CS_COMMANDObj *self, char *name)
{
    PyObject *rv;

    rv = PyMember_Get((char *)self, CS_COMMAND_memberlist, name);
    if (rv)
	return rv;
    PyErr_Clear();
    return Py_FindMethod(CS_COMMAND_methods, (PyObject *)self, name);
}

static int CS_COMMAND_setattr(CS_COMMANDObj *self, char *name, PyObject *v)
{
    if (v == NULL) {
	PyErr_SetString(PyExc_AttributeError, "Cannot delete attribute");
	return -1;
    }
    return PyMember_Set((char *)self, CS_COMMAND_memberlist, name, v);
}

static char CS_COMMANDType__doc__[] = 
"";

PyTypeObject CS_COMMANDType = {
    PyObject_HEAD_INIT(0)
    0,				/*ob_size*/
    "CommandType",		/*tp_name*/
    sizeof(CS_COMMANDObj),	/*tp_basicsize*/
    0,				/*tp_itemsize*/
    /* methods */
    (destructor)CS_COMMAND_dealloc,/*tp_dealloc*/
    (printfunc)0,		/*tp_print*/
    (getattrfunc)CS_COMMAND_getattr, /*tp_getattr*/
    (setattrfunc)CS_COMMAND_setattr, /*tp_setattr*/
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
    CS_COMMANDType__doc__	/* Documentation string */
};
