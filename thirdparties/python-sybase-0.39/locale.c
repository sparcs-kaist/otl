/******************************************************************

 Copyright 2001 by Object Craft P/L, Melbourne, Australia.

 LICENCE - see LICENCE file distributed with this software for details.

******************************************************************/

#include "sybasect.h"

static int locale_serial;

PyObject *locale_alloc(CS_CONTEXTObj *ctx)
{
    CS_LOCALEObj *self;
    CS_RETCODE status;
    CS_LOCALE *loc;

    self = PyObject_NEW(CS_LOCALEObj, &CS_LOCALEType);
    if (self == NULL)
	return NULL;

    SY_LEAK_REG(self);
    self->locale = NULL;
    self->debug = ctx->debug;
    self->serial = locale_serial++;

    /* PyErr_Clear(); */

    SY_CTX_BEGIN_THREADS(ctx);
    status = cs_loc_alloc(ctx->ctx, &loc);
    SY_CTX_END_THREADS(ctx);

    if (self->debug)
	debug_msg("cs_loc_alloc(ctx%d, &loc) -> %s",
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

    self->ctx = ctx;
    Py_INCREF(self->ctx);
    self->locale = loc;

    if (self->debug)
	debug_msg(", locale%d\n", self->serial);
    return Py_BuildValue("iN", CS_SUCCEED, self);
}

static void CS_LOCALE_dealloc(CS_LOCALEObj *self)
{
    SY_LEAK_UNREG(self);

    if (self->locale) {
	/* should check return == CS_SUCCEED, but we can't handle failure
	   here */
	CS_RETCODE status;

	status = cs_loc_drop(self->ctx->ctx, self->locale);
	if (self->debug)
	    debug_msg("cs_loc_drop(ctx%d, locale%d) -> %s\n",
		      self->ctx->serial, self->serial,
		      value_str(VAL_STATUS, status));
    }
    Py_XDECREF(self->ctx);
    PyObject_DEL(self);
}

static int csdate_type(int type)
{
    switch (type) {
    case CS_12HOUR:
	return OPTION_BOOL;
    case CS_DT_CONVFMT:
	return OPTION_INT;
    case CS_MONTH:
    case CS_SHORTMONTH:
    case CS_DAYNAME:
    case CS_DATEORDER:
	return OPTION_STRING;
    default:
	return OPTION_UNKNOWN;
    }
}

static char CS_LOCALE_cs_dt_info__doc__[] = 
"cs_dt_info(CS_SET, type, value) -> status\n"
"cs_dt_info(CS_GET, type [, item]) -> status, value";

static PyObject *CS_LOCALE_cs_dt_info(CS_LOCALEObj *self, PyObject *args)
{
    int action, type;
    PyObject *obj = NULL;
    CS_RETCODE status;
    CS_INT int_value, out_len, item, buff_len;
    CS_BOOL bool_value;
    char str_buff[10240];

    if (!first_tuple_int(args, &action))
	return NULL;

    switch (action) {
    case CS_SET:
	/* cs_dt_info(CS_SET, type, value) -> status */
	if (!PyArg_ParseTuple(args, "iiO", &action, &type, &obj))
	    return NULL;
	int_value = PyInt_AsLong(obj);
	if (PyErr_Occurred())
	    return NULL;

	status = cs_dt_info(self->ctx->ctx, CS_SET, self->locale,
			    type, CS_UNUSED,
			    &int_value, sizeof(int_value), &out_len);
	if (self->debug) {
	    if (type == CS_DT_CONVFMT)
		debug_msg("cs_dt_info(ctx%d, CS_SET, locale%d, %s, CS_UNUSED, %s, %d, &outlen) -> %s\n",
			  self->ctx->serial, self->serial,
			  value_str(VAL_DTINFO, type),
			  value_str(VAL_CSDATES, int_value), sizeof(int_value),
			  value_str(VAL_STATUS, status));
	    else
		debug_msg("cs_dt_info(ctx%d, CS_SET, locale%d, %s, CS_UNUSED, %d, %d, &outlen) -> %s\n",
			  self->ctx->serial, self->serial,
			  value_str(VAL_DTINFO, type),
			  (int)int_value, sizeof(int_value),
			  value_str(VAL_STATUS, status));
	}

	return PyInt_FromLong(status);

    case CS_GET:
	/* cs_dt_info(CS_GET, type [, item]) -> status, value */
	item = CS_UNUSED;
	if (!PyArg_ParseTuple(args, "ii|i", &action, &type, &item))
	    return NULL;

	switch (csdate_type(type)) {
	case OPTION_BOOL:
	    status = cs_dt_info(self->ctx->ctx, CS_GET, self->locale,
				type, CS_UNUSED,
				&bool_value, sizeof(bool_value), &out_len);
	    if (self->debug)
		debug_msg("cs_dt_info(ctx%d, CS_GET, locale%d, %s, CS_UNUSED, &value, %d, &outlen) -> %s, %d\n",
			  self->ctx->serial, self->serial,
			  value_str(VAL_DTINFO, type), sizeof(bool_value),
			  value_str(VAL_STATUS, status), (int)bool_value);
	    return Py_BuildValue("ii", status, bool_value);

	case OPTION_INT:
	    status = cs_dt_info(self->ctx->ctx, CS_GET, self->locale,
				type, CS_UNUSED,
				&int_value, sizeof(int_value), &out_len);
	    if (self->debug) {
		if (type == CS_DT_CONVFMT)
		    debug_msg("cs_dt_info(ctx%d, CS_GET, locale%d, %s, CS_UNUSED, &value, %d, &outlen) -> %s, %s\n",
			      self->ctx->serial, self->serial,
			      value_str(VAL_DTINFO, type), sizeof(int_value),
			      value_str(VAL_STATUS, status),
			      value_str(VAL_CSDATES, int_value));
		else
		    debug_msg("cs_dt_info(ctx%d, CS_GET, locale%d, %s, CS_UNUSED, &value, %d, &outlen) -> %s, %d\n",
			      self->ctx->serial, self->serial,
			      value_str(VAL_DTINFO, type), sizeof(int_value),
			      value_str(VAL_STATUS, status), (int)int_value);
	    }
	    return Py_BuildValue("ii", status, int_value);

	case OPTION_STRING:
	    status = cs_dt_info(self->ctx->ctx, CS_GET, self->locale,
				type, item,
				str_buff, sizeof(str_buff), &buff_len);
	    if (buff_len > sizeof(str_buff))
		buff_len = sizeof(str_buff);
	    if (self->debug)
		debug_msg("cs_dt_info(ctx%d, CS_GET, locale%d, %s, %d, buff, %d, &outlen) -> %s, \"%.*s\"\n",
			  self->ctx->serial, self->serial,
			  value_str(VAL_DTINFO, type), (int)item, sizeof(str_buff),
			  value_str(VAL_STATUS, status), (int)buff_len, str_buff);
	    return Py_BuildValue("is", status, str_buff);

	case OPTION_UNKNOWN:
	    PyErr_SetString(PyExc_TypeError, "unknown option type");
	    return NULL;

	default:
	    PyErr_SetString(PyExc_TypeError, "unhandled property value");
	    return NULL;
	}

    default:
	PyErr_SetString(PyExc_TypeError, "unknown action");
	return NULL;
    }
}

static char CS_LOCALE_cs_loc_drop__doc__[] = 
"cs_loc_drop() -> status";

static PyObject *CS_LOCALE_cs_loc_drop(CS_LOCALEObj *self, PyObject *args)
{
    CS_RETCODE status;

    if (!PyArg_ParseTuple(args, ""))
	return NULL;

    if (self->locale == NULL) {
	PyErr_SetString(PyExc_TypeError, "CS_LOCALE has been dropped");
	return NULL;
    }

    SY_CTX_BEGIN_THREADS(self->ctx);
    status = cs_loc_drop(self->ctx->ctx, self->locale);
    SY_CTX_END_THREADS(self->ctx);

    if (self->debug)
	debug_msg("cs_loc_drop(ctx%d, locale%d) -> %s\n",
		  self->ctx->serial, self->serial,
		  value_str(VAL_STATUS, status));

    if (status == CS_SUCCEED)
	self->locale = NULL;

    return PyInt_FromLong(status);
}

static char CS_LOCALE_cs_locale__doc__[] = 
"cs_locale(CS_SET, type, str) -> status\n"
"cs_locale(CS_GET, type) -> status, str\n";

static PyObject *CS_LOCALE_cs_locale(CS_LOCALEObj *self, PyObject *args)
{
    int action, type;
    CS_INT str_len;
    char *str;
    char buff[1024];
    CS_RETCODE status;

    if (!first_tuple_int(args, &action))
	return NULL;

    switch (action) {
    case CS_SET:
	/* cs_locale(CS_SET, type, str) -> status */
	if (!PyArg_ParseTuple(args, "iis", &action, &type, &str))
	    return NULL;

	/* PyErr_Clear(); */

	status = cs_locale(self->ctx->ctx, CS_SET, self->locale,
			   type, str, CS_NULLTERM, NULL);

	if (PyErr_Occurred())
	    return NULL;

	return PyInt_FromLong(status);

    case CS_GET:
	/* cs_locale(CS_GET, type) -> status, str */
	if (!PyArg_ParseTuple(args, "ii", &action, &type))
	    return NULL;

	/* PyErr_Clear(); */
	status = cs_locale(self->ctx->ctx, CS_GET, self->locale,
			   type, buff, sizeof(buff), &str_len);
	if (PyErr_Occurred())
	    return NULL;

	return Py_BuildValue("is", status, buff);

    default:
	PyErr_SetString(PyExc_TypeError, "unknown type");
	return NULL;
    }
}

static struct PyMethodDef CS_LOCALE_methods[] = {
    { "cs_dt_info", (PyCFunction)CS_LOCALE_cs_dt_info, METH_VARARGS, CS_LOCALE_cs_dt_info__doc__ },
    { "cs_loc_drop", (PyCFunction)CS_LOCALE_cs_loc_drop, METH_VARARGS, CS_LOCALE_cs_loc_drop__doc__ },
    { "cs_locale", (PyCFunction)CS_LOCALE_cs_locale, METH_VARARGS, CS_LOCALE_cs_locale__doc__ },
    { NULL }
};

static PyObject *CS_LOCALE_getattr(CS_LOCALEObj *self, char *name)
{
    return Py_FindMethod(CS_LOCALE_methods, (PyObject *)self, name);
}

static char CS_LOCALEType__doc__[] = 
"";

PyTypeObject CS_LOCALEType = {
    PyObject_HEAD_INIT(0)
    0,				/*ob_size*/
    "LocaleType",		/*tp_name*/
    sizeof(CS_LOCALEObj),	/*tp_basicsize*/
    0,				/*tp_itemsize*/
    /* methods */
    (destructor)CS_LOCALE_dealloc,/*tp_dealloc*/
    (printfunc)0,		/*tp_print*/
    (getattrfunc)CS_LOCALE_getattr, /*tp_getattr*/
    (setattrfunc)0,		/*tp_setattr*/
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
    CS_LOCALEType__doc__	/* Documentation string */
};
