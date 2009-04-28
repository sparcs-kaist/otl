/******************************************************************

 Copyright 2001 by Object Craft P/L, Melbourne, Australia.

 LICENCE - see LICENCE file distributed with this software for details.

******************************************************************/

#include "sybasect.h"

PyTypeObject DateTimeType;

static int datetime_crack(DateTimeObj *self)
{
    CS_RETCODE crack_result = CS_SUCCEED;
    CS_CONTEXT *ctx;

    ctx = global_ctx();
    if (ctx == NULL)
	return CS_FAIL;

    if (self->type == CS_DATETIME_TYPE)
	crack_result = cs_dt_crack(ctx, self->type,
				   &self->v.datetime, &self->daterec);
    else
	crack_result = cs_dt_crack(ctx, self->type,
				   &self->v.datetime4, &self->daterec);
    self->cracked = 1;
    return crack_result;
}

static struct PyMethodDef DateTime_methods[] = {
    { NULL }			/* sentinel */
};

int datetime_assign(PyObject *obj, int type, void *buff)
{
    CS_DATAFMT src_fmt;
    CS_DATAFMT dest_fmt;
    void *src_buff;
    CS_RETCODE conv_result;
    CS_INT datetime_len;
    CS_CONTEXT *ctx;

    if (((DateTimeObj*)obj)->type == type) {
	if (type == CS_DATETIME_TYPE)
	    *(CS_DATETIME*)buff = ((DateTimeObj*)obj)->v.datetime;
	else
	    *(CS_DATETIME4*)buff = ((DateTimeObj*)obj)->v.datetime4;
	return CS_SUCCEED;
    }
    datetime_datafmt(&src_fmt, ((DateTimeObj*)obj)->type);
    datetime_datafmt(&dest_fmt, type);

    if (((DateTimeObj*)obj)->type == CS_DATETIME_TYPE)
	src_buff = &((DateTimeObj*)obj)->v.datetime;
    else
	src_buff = &((DateTimeObj*)obj)->v.datetime4;

    /* PyErr_Clear(); */

    ctx = global_ctx();
    if (ctx == NULL)
	return CS_FAIL;

    conv_result = cs_convert(ctx,
			     &src_fmt, src_buff,
			     &dest_fmt, buff, &datetime_len);
    if (PyErr_Occurred())
	return CS_FAIL;
    if (conv_result != CS_SUCCEED)
	PyErr_SetString(PyExc_TypeError, "datetime conversion failed");
    return conv_result;
}

int datetime_as_string(PyObject *obj, char *text)
{
    CS_DATAFMT datetime_fmt;
    CS_DATAFMT char_fmt;
    CS_INT char_len;
    CS_CONTEXT *ctx;
    int type;
    void *data;

    type = ((DateTimeObj*)obj)->type;
    datetime_datafmt(&datetime_fmt, type);
    char_datafmt(&char_fmt);
    char_fmt.maxlength = DATETIME_LEN;

    if (type == CS_DATETIME_TYPE)
	data = &((DateTimeObj*)obj)->v.datetime;
    else
	data = &((DateTimeObj*)obj)->v.datetime4;
    ctx = global_ctx();
    if (ctx == NULL)
	return CS_FAIL;

    return cs_convert(ctx,
		      &datetime_fmt, data,
		      &char_fmt, text, &char_len);
}

PyObject *datetime_alloc(void *value, int type)
{
    DateTimeObj *self;

    self = PyObject_NEW(DateTimeObj, &DateTimeType);
    if (self == NULL)
	return NULL;

    SY_LEAK_REG(self);
    self->type = type;
    if (type == CS_DATETIME_TYPE)
	memcpy(&self->v.datetime, value, sizeof(self->v.datetime));
    else
	memcpy(&self->v.datetime4, value, sizeof(self->v.datetime4));
    memset(&self->daterec, 0, sizeof(self->daterec));
    self->cracked = 0;
    return (PyObject*)self;
}

PyObject *DateTime_FromString(PyObject *obj)
{
    CS_DATAFMT datetime_fmt;
    CS_DATAFMT char_fmt;
    CS_DATETIME datetime;
    CS_INT datetime_len;
    CS_CONTEXT *ctx;
    char *str = PyString_AsString(obj);
    CS_RETCODE conv_result;

    datetime_datafmt(&datetime_fmt, CS_DATETIME_TYPE);
    char_datafmt(&char_fmt);
    char_fmt.maxlength = strlen(str);

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return NULL;
    conv_result = cs_convert(ctx,
			     &char_fmt, str,
			     &datetime_fmt, &datetime, &datetime_len);
    if (PyErr_Occurred())
	return NULL;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "datetime from string conversion failed");
	return NULL;
    }

    return datetime_alloc(&datetime, CS_DATETIME_TYPE);
}

PyObject *DateTime_FromPyDateTime(PyObject *obj)
{
#ifdef HAVE_DATETIME
    PyObject *res;
    PyObject *str;

    str = PyObject_Str(obj);
    if (PyErr_Occurred())
	return NULL;

    res = DateTime_FromString(str);
    Py_XDECREF(str);
    return res;
#else
    PyErr_SetString(PyExc_TypeError, "python-sybase compiled without support for python datetime");
    return NULL;
#endif
}

static void DateTime_dealloc(DateTimeObj *self)
{
    SY_LEAK_UNREG(self);

    PyObject_DEL(self);
}

static PyObject *DateTime_repr(DateTimeObj *self)
{
    char text[DATETIME_LEN + 2];
    CS_RETCODE conv_result;

    /* PyErr_Clear(); */
    conv_result = datetime_as_string((PyObject*)self, text + 1);
    if (PyErr_Occurred())
	return NULL;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "datetime to string conversion failed");
	return NULL;
    }

    text[0] = '\'';
    strcat(text, "'");
    return PyString_FromString(text);
}

static PyObject *DateTime_str(DateTimeObj *self)
{
    char text[DATETIME_LEN + 2];
    CS_RETCODE conv_result;

    /* PyErr_Clear(); */
    conv_result = datetime_as_string((PyObject*)self, text);
    if (PyErr_Occurred())
	return NULL;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "datetime to string conversion failed");
	return NULL;
    }

    return PyString_FromString(text);
}

static PyObject *DateTime_int(DateTimeObj *v)
{
    CS_DATAFMT datetime_fmt;
    CS_DATAFMT int_fmt;
    CS_INT int_value;
    CS_INT int_len;
    CS_CONTEXT *ctx;
    void *value;
    CS_RETCODE conv_result;

    datetime_datafmt(&datetime_fmt, v->type);
    int_datafmt(&int_fmt);

    if (v->type == CS_DATETIME_TYPE)
	value = &v->v.datetime;
    else
	value = &v->v.datetime4;

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return NULL;
    conv_result = cs_convert(ctx, &datetime_fmt, value,
			     &int_fmt, &int_value, &int_len);
    if (PyErr_Occurred())
	return NULL;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "int conversion failed");
	return NULL;
    }

    return PyInt_FromLong(int_value);
}

static PyObject *DateTime_long(DateTimeObj *v)
{
    char *end;
    char text[DATETIME_LEN];
    CS_RETCODE conv_result;

    /* PyErr_Clear(); */
    conv_result = datetime_as_string((PyObject*)v, text);
    if (PyErr_Occurred())
	return NULL;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "datetime to string conversion failed");
	return NULL;
    }

    return PyLong_FromString(text, &end, 10);
}

static PyObject *DateTime_float(DateTimeObj *v)
{
    CS_DATAFMT datetime_fmt;
    CS_DATAFMT float_fmt;
    CS_FLOAT float_value;
    CS_INT float_len;
    CS_CONTEXT *ctx;
    void *value;
    CS_RETCODE conv_result;

    datetime_datafmt(&datetime_fmt, v->type);
    float_datafmt(&float_fmt);

    if (v->type == CS_DATETIME_TYPE)
	value = &v->v.datetime;
    else
	value = &v->v.datetime4;

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return NULL;
    conv_result = cs_convert(ctx, &datetime_fmt, value,
			     &float_fmt, &float_value, &float_len);
    if (PyErr_Occurred())
	return NULL;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "float conversion failed");
	return NULL;
    }

    return PyFloat_FromDouble(float_value);
}

static PyNumberMethods DateTime_as_number = {
    (binaryfunc)0,		/*nb_add*/
    (binaryfunc)0,		/*nb_subtract*/
    (binaryfunc)0,		/*nb_multiply*/
    (binaryfunc)0,		/*nb_divide*/
    (binaryfunc)0,		/*nb_remainder*/
    (binaryfunc)0,		/*nb_divmod*/
    (ternaryfunc)0,		/*nb_power*/
    (unaryfunc)0,		/*nb_negative*/
    (unaryfunc)0,		/*nb_positive*/
    (unaryfunc)0,		/*nb_absolute*/
    (inquiry)0,			/*nb_nonzero*/
    (unaryfunc)0,		/*nb_invert*/
    (binaryfunc)0,		/*nb_lshift*/
    (binaryfunc)0,		/*nb_rshift*/
    (binaryfunc)0,		/*nb_and*/
    (binaryfunc)0,		/*nb_xor*/
    (binaryfunc)0,		/*nb_or*/
    (coercion)0,		/*nb_coerce*/
    (unaryfunc)DateTime_int,	/*nb_int*/
    (unaryfunc)DateTime_long,	/*nb_long*/
    (unaryfunc)DateTime_float,	/*nb_float*/
    (unaryfunc)0,		/*nb_oct*/
    (unaryfunc)0,		/*nb_hex*/
};

#define OFFSET(x) offsetof(DateTimeObj, x)

static struct memberlist DateTime_memberlist[] = {
    { "type",      T_INT, OFFSET(type), RO },
    { "year",      T_INT, OFFSET(daterec.dateyear), RO },
    { "month",     T_INT, OFFSET(daterec.datemonth), RO },
    { "day",       T_INT, OFFSET(daterec.datedmonth), RO },
    { "dayofyear", T_INT, OFFSET(daterec.datedyear), RO },
    { "weekday",   T_INT, OFFSET(daterec.datedweek), RO },
    { "hour",      T_INT, OFFSET(daterec.datehour), RO },
    { "minute",    T_INT, OFFSET(daterec.dateminute), RO },
    { "second",    T_INT, OFFSET(daterec.datesecond), RO },
    { "msecond",   T_INT, OFFSET(daterec.datemsecond), RO },
    { "tzone",     T_INT, OFFSET(daterec.datetzone), RO },
    { NULL }
};

static PyObject *DateTime_getattr(DateTimeObj *self, char *name)
{
    PyObject *rv;

    if (!self->cracked && strcmp(name, "type") != 0) {
	CS_RETCODE crack_result;

	/* PyErr_Clear(); */
	crack_result = datetime_crack(self);
	if (PyErr_Occurred())
	    return NULL;
	if (crack_result != CS_SUCCEED) {
	    PyErr_SetString(PyExc_TypeError, "datetime crack failed");
	    return NULL;
	}
    }

    rv = PyMember_Get((char*)self, DateTime_memberlist, name);
    if (rv)
	return rv;
    PyErr_Clear();
    return Py_FindMethod(DateTime_methods, (PyObject *)self, name);
}

static int DateTime_setattr(DateTimeObj *self, char *name, PyObject *v)
{
    if (v == NULL) {
	PyErr_SetString(PyExc_AttributeError, "Cannot delete attribute");
	return -1;
    }
    return PyMember_Set((char*)self, DateTime_memberlist, name, v);
}

static char DateTimeType__doc__[] = 
"";

PyTypeObject DateTimeType = {
    PyObject_HEAD_INIT(0)
    0,				/*ob_size*/
    "DateTimeType",		/*tp_name*/
    sizeof(DateTimeObj),	/*tp_basicsize*/
    0,				/*tp_itemsize*/
    /* methods */
    (destructor)DateTime_dealloc,/*tp_dealloc*/
    (printfunc)0,		/*tp_print*/
    (getattrfunc)DateTime_getattr, /*tp_getattr*/
    (setattrfunc)DateTime_setattr, /*tp_setattr*/
    (cmpfunc)0,			/*tp_compare*/
    (reprfunc)DateTime_repr,	/*tp_repr*/
    &DateTime_as_number,	/*tp_as_number*/
    0,				/*tp_as_sequence*/
    0,				/*tp_as_mapping*/
    (hashfunc)0,		/*tp_hash*/
    (ternaryfunc)0,		/*tp_call*/
    (reprfunc)DateTime_str,	/*tp_str*/

    /* Space for future expansion */
    0L,0L,0L,0L,
    DateTimeType__doc__		/* Documentation string */
};

char DateTimeType_new__doc__[] =
"datetime(s [, type = CS_DATETIME_TYPE]) -> DateTime\n"
"\n"
"Create a datetime object.";

/* Implement the mssqldb.datetime() method
 */
PyObject *DateTimeType_new(PyObject *module, PyObject *args)
{
    CS_DATAFMT datetime_fmt;
    CS_DATAFMT char_fmt;
    CS_CONTEXT *ctx;
    int type = CS_DATETIME_TYPE;
    char *str;
    CS_DATETIME datetime;
    CS_INT datetime_len;
    CS_RETCODE conv_result;

    if (!PyArg_ParseTuple(args, "s|i", &str, &type))
	return NULL;

    datetime_datafmt(&datetime_fmt, type);
    char_datafmt(&char_fmt);
    char_fmt.maxlength = strlen(str);

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return NULL;
    conv_result = cs_convert(ctx,
			     &char_fmt, str,
			     &datetime_fmt, &datetime, &datetime_len);
    if (PyErr_Occurred())
	return NULL;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "datetime from string conversion failed");
	return NULL;
    }

    return datetime_alloc(&datetime, type);
}

/* Used in unpickler
 */
static PyObject *datetime_constructor = NULL;

/* Register the datetime type with the copy_reg module.  This allows
 * Python to (un)pickle datetime objects.  The equivalent Python code
 * is this:
 *
 * def pickle_datetime(dt):
 *     return datetime, (str(dt), dt.type)
 * 
 * copy_reg.pickle(type(datetime(1)), pickle_datetime, datetime)
 */
char pickle_datetime__doc__[] =
"pickle_datetime(dt) -> datetime, (str(dt), dt.type)\n"
"\n"
"Used to pickle the datetime data type.";

/* DateTime pickling function
 */
PyObject *pickle_datetime(PyObject *module, PyObject *args)
{
    DateTimeObj *obj = NULL;
    PyObject *values = NULL,
	*tuple = NULL;
    char text[DATETIME_LEN];

    if (!PyArg_ParseTuple(args, "O!", &DateTimeType, &obj))
	goto error;
    if (datetime_as_string((PyObject*)obj, text) != CS_SUCCEED)
	goto error;
    if ((values = Py_BuildValue("(si)", text, obj->type)) == NULL)
	goto error;
    tuple = Py_BuildValue("(OO)", datetime_constructor, values);

error:
    Py_XDECREF(values);
    return tuple;
}

/* Register DateTime type pickler
 */
int copy_reg_datetime(PyObject *dict)
{
    PyObject *module = NULL,
	*pickle_func = NULL,
	*pickler = NULL,
	*obj = NULL;

    module = PyImport_ImportModule("copy_reg");
    if (module == NULL)
	goto error;
    if ((pickle_func = PyObject_GetAttrString(module, "pickle")) == NULL)
	goto error;
    if ((datetime_constructor = PyDict_GetItemString(dict, "datetime")) == NULL)
	goto error;
    if ((pickler = PyDict_GetItemString(dict, "pickle_datetime")) == NULL)
	goto error;
    obj = PyObject_CallFunction(pickle_func, "OOO",
				&DateTimeType, pickler, datetime_constructor);

error:
    Py_XDECREF(obj);
    Py_XDECREF(pickle_func);
    Py_XDECREF(module);

    return (obj == NULL) ? -1 : 0;
}
