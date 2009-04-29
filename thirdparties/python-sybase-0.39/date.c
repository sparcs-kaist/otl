/******************************************************************

 Copyright 2001 by Sungard GP3, Paris, France.

 LICENCE - see LICENCE file distributed with this software for details.

******************************************************************/

#include "sybasect.h"

#ifdef CS_DATE_TYPE

PyTypeObject DateType;

/* Convert a machine-readable datetime value into a user-accessible format. */
static int date_crack(DateObj *self)
{
    CS_RETCODE crack_result = CS_SUCCEED;
    CS_CONTEXT *ctx;

    ctx = global_ctx();
    if (ctx == NULL)
	return CS_FAIL;

    crack_result = cs_dt_crack(ctx, self->type,
			       &self->date, &self->daterec);
    self->cracked = 1;
    return crack_result;
}

static struct PyMethodDef Date_methods[] = {
    { NULL }			/* sentinel */
};

int date_assign(PyObject *obj, int type, void *buff)
{
    CS_DATAFMT src_fmt;
    CS_DATAFMT dest_fmt;
    void *src_buff;
    CS_RETCODE conv_result;
    CS_INT date_len;
    CS_CONTEXT *ctx;

    if (((DateObj*)obj)->type == type) {
	*(CS_DATE*)buff = ((DateObj*)obj)->date;
	return CS_SUCCEED;
    }
    date_datafmt(&src_fmt);
    date_datafmt(&dest_fmt);

    src_buff = &((DateObj*)obj)->date;

    /* PyErr_Clear(); */

    ctx = global_ctx();
    if (ctx == NULL)
	return CS_FAIL;

    conv_result = cs_convert(ctx,
			     &src_fmt, src_buff,
			     &dest_fmt, buff, &date_len);
    if (PyErr_Occurred())
	return CS_FAIL;
    if (conv_result != CS_SUCCEED)
	PyErr_SetString(PyExc_TypeError, "date conversion failed");
    return conv_result;
}

int date_as_string(PyObject *obj, char *text)
{
    CS_DATAFMT date_fmt;
    CS_DATAFMT char_fmt;
    CS_INT char_len;
    CS_CONTEXT *ctx;
    void *data;

    date_datafmt(&date_fmt);
    char_datafmt(&char_fmt);
    char_fmt.maxlength = DATE_LEN;

    data = &((DateObj*)obj)->date;
    ctx = global_ctx();
    if (ctx == NULL)
	return CS_FAIL;

    return cs_convert(ctx,
		      &date_fmt, data,
		      &char_fmt, text, &char_len);
}

PyObject *date_alloc(void *value)
{
    DateObj *self;

    self = PyObject_NEW(DateObj, &DateType);
    if (self == NULL)
	return NULL;

    SY_LEAK_REG(self);
    self->type = CS_DATE_TYPE;
    memcpy(&self->date, value, sizeof(self->date));
    memset(&self->daterec, 0, sizeof(self->daterec));
    self->cracked = 0;
    return (PyObject*)self;
}

PyObject *Date_FromString(PyObject *obj)
{
    CS_DATAFMT date_fmt;
    CS_DATAFMT char_fmt;
    CS_DATE date;
    CS_INT date_len;
    CS_CONTEXT *ctx;
    char *str = PyString_AsString(obj);
    CS_RETCODE conv_result;

    date_datafmt(&date_fmt);
    char_datafmt(&char_fmt);
    char_fmt.maxlength = strlen(str);

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return NULL;
    conv_result = cs_convert(ctx,
			     &char_fmt, str,
			     &date_fmt, &date, &date_len);
    if (PyErr_Occurred())
	return NULL;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "date from string conversion failed");
	return NULL;
    }

    return date_alloc(&date);
}

PyObject *Date_FromPyDate(PyObject *obj)
{
#ifdef HAVE_DATETIME
    PyObject *res;
    PyObject *str;

    str = PyObject_Str(obj);
    if (PyErr_Occurred())
	return NULL;

    res = Date_FromString(str);
    Py_XDECREF(str);
    return res;
#else
    PyErr_SetString(PyExc_TypeError, "python-sybase compiled without support for python datetime");
    return NULL;
#endif
}

static void Date_dealloc(DateObj *self)
{
    SY_LEAK_UNREG(self);

    PyObject_DEL(self);
}

static PyObject *Date_repr(DateObj *self)
{
    char text[DATE_LEN + 2];
    CS_RETCODE conv_result;

    /* PyErr_Clear(); */
    conv_result = date_as_string((PyObject*)self, text + 1);
    if (PyErr_Occurred())
	return NULL;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "date to string conversion failed");
	return NULL;
    }

    text[0] = '\'';
    strcat(text, "'");
    return PyString_FromString(text);
}

static PyObject *Date_str(DateObj *self)
{
    char text[DATE_LEN + 2];
    CS_RETCODE conv_result;

    /* PyErr_Clear(); */
    conv_result = date_as_string((PyObject*)self, text);
    if (PyErr_Occurred())
	return NULL;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "date to string conversion failed");
	return NULL;
    }

    return PyString_FromString(text);
}

static PyObject *Date_int(DateObj *v)
{
    CS_DATAFMT date_fmt;
    CS_DATAFMT int_fmt;
    CS_INT int_value;
    CS_INT int_len;
    CS_CONTEXT *ctx;
    void *value;
    CS_RETCODE conv_result;

    date_datafmt(&date_fmt);
    int_datafmt(&int_fmt);

    value = &v->date;

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return NULL;
    conv_result = cs_convert(ctx, &date_fmt, value,
			     &int_fmt, &int_value, &int_len);
    if (PyErr_Occurred())
	return NULL;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "int conversion failed");
	return NULL;
    }

    return PyInt_FromLong(int_value);
}

static PyObject *Date_long(DateObj *v)
{
    char *end;
    char text[DATE_LEN];
    CS_RETCODE conv_result;

    /* PyErr_Clear(); */
    conv_result = date_as_string((PyObject*)v, text);
    if (PyErr_Occurred())
	return NULL;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "date to string conversion failed");
	return NULL;
    }

    return PyLong_FromString(text, &end, 10);
}

static PyObject *Date_float(DateObj *v)
{
    CS_DATAFMT date_fmt;
    CS_DATAFMT float_fmt;
    CS_FLOAT float_value;
    CS_INT float_len;
    CS_CONTEXT *ctx;
    void *value;
    CS_RETCODE conv_result;

    date_datafmt(&date_fmt);
    float_datafmt(&float_fmt);

    value = &v->date;

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return NULL;
    conv_result = cs_convert(ctx, &date_fmt, value,
			     &float_fmt, &float_value, &float_len);
    if (PyErr_Occurred())
	return NULL;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "float conversion failed");
	return NULL;
    }

    return PyFloat_FromDouble(float_value);
}

static PyNumberMethods Date_as_number = {
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
    (unaryfunc)Date_int,	/*nb_int*/
    (unaryfunc)Date_long,	/*nb_long*/
    (unaryfunc)Date_float,	/*nb_float*/
    (unaryfunc)0,		/*nb_oct*/
    (unaryfunc)0,		/*nb_hex*/
};

#define OFFSET(x) offsetof(DateObj, x)

static struct memberlist Date_memberlist[] = {
    { "type",      T_INT, OFFSET(type), RO },
    { "year",      T_INT, OFFSET(daterec.dateyear), RO },
    { "month",     T_INT, OFFSET(daterec.datemonth), RO },
    { "day",       T_INT, OFFSET(daterec.datedmonth), RO },
    { "dayofyear", T_INT, OFFSET(daterec.datedyear), RO },
    { "weekday",   T_INT, OFFSET(daterec.datedweek), RO },
    { "tzone",     T_INT, OFFSET(daterec.datetzone), RO },
    { NULL }
};

static PyObject *Date_getattr(DateObj *self, char *name)
{
    PyObject *rv;

    if (!self->cracked && strcmp(name, "type") != 0) {
	CS_RETCODE crack_result;

	/* PyErr_Clear(); */
	crack_result = date_crack(self);
	if (PyErr_Occurred())
	    return NULL;
	if (crack_result != CS_SUCCEED) {
	    PyErr_SetString(PyExc_TypeError, "date crack failed");
	    return NULL;
	}
    }

    rv = PyMember_Get((char*)self, Date_memberlist, name);
    if (rv)
	return rv;
    PyErr_Clear();
    return Py_FindMethod(Date_methods, (PyObject *)self, name);
}

static int Date_setattr(DateObj *self, char *name, PyObject *v)
{
    if (v == NULL) {
	PyErr_SetString(PyExc_AttributeError, "Cannot delete attribute");
	return -1;
    }
    return PyMember_Set((char*)self, Date_memberlist, name, v);
}

static char DateType__doc__[] = 
"";

PyTypeObject DateType = {
    PyObject_HEAD_INIT(0)
    0,				/*ob_size*/
    "DateType",		/*tp_name*/
    sizeof(DateObj),	/*tp_basicsize*/
    0,				/*tp_itemsize*/
    /* methods */
    (destructor)Date_dealloc,/*tp_dealloc*/
    (printfunc)0,		/*tp_print*/
    (getattrfunc)Date_getattr, /*tp_getattr*/
    (setattrfunc)Date_setattr, /*tp_setattr*/
    (cmpfunc)0,			/*tp_compare*/
    (reprfunc)Date_repr,	/*tp_repr*/
    &Date_as_number,	/*tp_as_number*/
    0,				/*tp_as_sequence*/
    0,				/*tp_as_mapping*/
    (hashfunc)0,		/*tp_hash*/
    (ternaryfunc)0,		/*tp_call*/
    (reprfunc)Date_str,	/*tp_str*/

    /* Space for future expansion */
    0L,0L,0L,0L,
    DateType__doc__		/* Documentation string */
};

char DateType_new__doc__[] =
"date(s [, type = CS_DATE_TYPE]) -> Date\n"
"\n"
"Create a date object.";

/* Implement the mssqldb.date() method
 */
PyObject *DateType_new(PyObject *module, PyObject *args)
{
    CS_DATAFMT date_fmt;
    CS_DATAFMT char_fmt;
    CS_CONTEXT *ctx;
    int type = CS_DATE_TYPE;
    char *str;
    CS_DATE date;
    CS_INT date_len;
    CS_RETCODE conv_result;

    if (!PyArg_ParseTuple(args, "s|i", &str, &type))
	return NULL;

    date_datafmt(&date_fmt);
    char_datafmt(&char_fmt);
    char_fmt.maxlength = strlen(str);

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return NULL;
    conv_result = cs_convert(ctx,
			     &char_fmt, str,
			     &date_fmt, &date, &date_len);
    if (PyErr_Occurred())
	return NULL;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "date from string conversion failed");
	return NULL;
    }

    return date_alloc(&date);
}

/* Used in unpickler
 */
static PyObject *date_constructor = NULL;

/* Register the date type with the copy_reg module.  This allows
 * Python to (un)pickle date objects.  The equivalent Python code
 * is this:
 *
 * def pickle_date(dt):
 *     return date, (str(dt), dt.type)
 * 
 * copy_reg.pickle(type(date(1)), pickle_date, date)
 */
char pickle_date__doc__[] =
"pickle_date(dt) -> date, (str(dt), dt.type)\n"
"\n"
"Used to pickle the date data type.";

/* Date pickling function
 */
PyObject *pickle_date(PyObject *module, PyObject *args)
{
    DateObj *obj = NULL;
    PyObject *values = NULL,
	*tuple = NULL;
    char text[DATE_LEN];

    if (!PyArg_ParseTuple(args, "O!", &DateType, &obj))
	goto error;
    if (date_as_string((PyObject*)obj, text) != CS_SUCCEED)
	goto error;
    if ((values = Py_BuildValue("(si)", text, obj->type)) == NULL)
	goto error;
    tuple = Py_BuildValue("(OO)", date_constructor, values);

error:
    Py_XDECREF(values);
    return tuple;
}

/* Register Date type pickler
 */
int copy_reg_date(PyObject *dict)
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
    if ((date_constructor = PyDict_GetItemString(dict, "date")) == NULL)
	goto error;
    if ((pickler = PyDict_GetItemString(dict, "pickle_date")) == NULL)
	goto error;
    obj = PyObject_CallFunction(pickle_func, "OOO",
				&DateType, pickler, date_constructor);

error:
    Py_XDECREF(obj);
    Py_XDECREF(pickle_func);
    Py_XDECREF(module);

    return (obj == NULL) ? -1 : 0;
}

#endif /* CS_DATE_TYPE */
