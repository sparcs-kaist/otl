/******************************************************************

 Copyright 2001 by Object Craft P/L, Melbourne, Australia.

 LICENCE - see LICENCE file distributed with this software for details.

******************************************************************/

#include "sybasect.h"

void money_datafmt(CS_DATAFMT *fmt, int type)
{
    memset(fmt, 0, sizeof(*fmt));
    fmt->datatype = CS_MONEY_TYPE;
    if (type == CS_MONEY_TYPE)
	fmt->maxlength = sizeof(CS_MONEY);
    else
	fmt->maxlength = sizeof(CS_MONEY4);
    fmt->locale = NULL;
    fmt->format = CS_FMT_UNUSED;
    fmt->precision = 0;
    fmt->scale = 0;
}

void datetime_datafmt(CS_DATAFMT *fmt, int type)
{
    memset(fmt, 0, sizeof(*fmt));
    fmt->datatype = type;
    if (type == CS_DATETIME_TYPE)
	fmt->maxlength = sizeof(CS_DATETIME);
    else
	fmt->maxlength = sizeof(CS_DATETIME4);
    fmt->locale = NULL;
    fmt->format = CS_FMT_UNUSED;
    fmt->precision = 0;
    fmt->scale = 0;
}

#ifdef CS_DATE_TYPE
void date_datafmt(CS_DATAFMT *fmt)
{
    memset(fmt, 0, sizeof(*fmt));
    fmt->datatype = CS_DATE_TYPE;
    fmt->maxlength = sizeof(CS_DATE);
    fmt->locale = NULL;
    fmt->format = CS_FMT_UNUSED;
    fmt->precision = 0;
    fmt->scale = 0;
}
#endif

void numeric_datafmt(CS_DATAFMT *fmt, int precision, int scale)
{
    memset(fmt, 0, sizeof(*fmt));
    fmt->datatype = CS_NUMERIC_TYPE;
    fmt->maxlength = sizeof(CS_NUMERIC);
    fmt->locale = NULL;
    fmt->format = CS_FMT_UNUSED;
    fmt->precision = (precision < 0) ? CS_SRC_VALUE : precision;
    fmt->scale = (scale < 0) ? CS_SRC_VALUE : scale;
}

void char_datafmt(CS_DATAFMT *fmt)
{
    memset(fmt, 0, sizeof(*fmt));
    fmt->datatype = CS_CHAR_TYPE;
    fmt->maxlength = NUMERIC_LEN;
    fmt->locale = NULL;
    fmt->format = CS_FMT_NULLTERM;
    fmt->scale = 0;
    fmt->precision = 0;
}

void int_datafmt(CS_DATAFMT *fmt)
{
    memset(fmt, 0, sizeof(*fmt));
    fmt->datatype = CS_INT_TYPE;
    fmt->maxlength = sizeof(CS_INT);
    fmt->locale = NULL;
    fmt->format = CS_FMT_UNUSED;
    fmt->scale = 0;
    fmt->precision = 0;
}

void long_datafmt(CS_DATAFMT *fmt)
{
    memset(fmt, 0, sizeof(*fmt));
    fmt->datatype = CS_LONG_TYPE;
    fmt->maxlength = sizeof(CS_LONG);
    fmt->locale = NULL;
    fmt->format = CS_FMT_UNUSED;
    fmt->scale = 0;
    fmt->precision = 0;
}

void float_datafmt(CS_DATAFMT *fmt)
{
    memset(fmt, 0, sizeof(*fmt));
    fmt->datatype = CS_FLOAT_TYPE;
    fmt->maxlength = sizeof(CS_FLOAT);
    fmt->locale = NULL;
    fmt->format = CS_FMT_UNUSED;
    fmt->scale = 0;
    fmt->precision = 0;
}

static struct PyMethodDef CS_DATAFMT_methods[] = {
    { NULL }			/* sentinel */
};

static int datafmt_serial;

PyObject *datafmt_alloc(CS_DATAFMT *datafmt, int strip)
{
    CS_DATAFMTObj *self;

    self = PyObject_NEW(CS_DATAFMTObj, &CS_DATAFMTType);
    if (self == NULL)
	return NULL;

    SY_LEAK_REG(self);
    self->strip = strip;
    self->fmt = *datafmt;
    self->serial = datafmt_serial++;

    return (PyObject*)self;
}

char datafmt_new__doc__[] =
"CS_DATAFMT() -> fmt\n"
"\n"
"Allocate a new CS_DATAFMT object.";

PyObject *datafmt_new(PyObject *module, PyObject *args)
{
    CS_DATAFMTObj *self;

    if (!PyArg_ParseTuple(args, ""))
	return NULL;

    self = PyObject_NEW(CS_DATAFMTObj, &CS_DATAFMTType);
    if (self == NULL)
	return NULL;

    SY_LEAK_REG(self);
    memset(&self->fmt, 0, sizeof(self->fmt));
    self->strip = 0;
    self->serial = datafmt_serial++;

    char_datafmt(&self->fmt);
    self->fmt.maxlength = 1;
    return (PyObject*)self;
}

static void CS_DATAFMT_dealloc(CS_DATAFMTObj *self)
{
    SY_LEAK_UNREG(self);
    PyObject_DEL(self);
}

void datafmt_debug(CS_DATAFMT *fmt)
{
    debug_msg("[name:\"%.*s\" type:%s status:%s format:%s count:%d"
	      " maxlength:%d scale:%d precision:%d]",
	      fmt->namelen, fmt->name,
	      value_str(VAL_TYPE, fmt->datatype),
	      value_str(VAL_STATUSFMT, fmt->status),
	      value_str(VAL_DATAFMT, fmt->format),
	      fmt->count, fmt->maxlength, fmt->scale, fmt->precision);
}

/* Code to access structure members by accessing attributes */

#define OFF(x) offsetof(CS_DATAFMTObj, x)

static struct memberlist CS_DATAFMT_memberlist[] = {
    { "name", T_STRING_INPLACE, OFF(fmt.name) }, /* faked */
    { "datatype", T_INT, OFF(fmt.datatype) },
    { "format", T_INT, OFF(fmt.format) },
    { "maxlength", T_INT, OFF(fmt.maxlength) },
    { "scale", T_INT, OFF(fmt.scale) },
    { "precision", T_INT, OFF(fmt.precision) },
    { "status", T_INT, OFF(fmt.status) },
    { "count", T_INT, OFF(fmt.count) },
    { "usertype", T_INT, OFF(fmt.usertype) },
    { "strip", T_INT, OFF(strip) },
    { NULL }			/* Sentinel */
};

static PyObject *CS_DATAFMT_getattr(CS_DATAFMTObj *self, char *name)
{
    PyObject *rv;

    if (strcmp(name, "name") == 0)
	return PyString_FromStringAndSize(self->fmt.name, self->fmt.namelen);

    rv = PyMember_Get((char *)self, CS_DATAFMT_memberlist, name);
    if (rv)
	return rv;
    PyErr_Clear();
    return Py_FindMethod(CS_DATAFMT_methods, (PyObject *)self, name);
}

static int CS_DATAFMT_setattr(CS_DATAFMTObj *self, char *name, PyObject *v)
{
    if (v == NULL) {
	PyErr_SetString(PyExc_AttributeError, "Cannot delete attribute");
	return -1;
    }
    if (strcmp(name, "name") == 0) {
	int size;

	if (!PyString_Check(v)) {
	    PyErr_BadArgument();
	    return -1;
	}
	size = PyString_Size(v);
	if (size > sizeof(self->fmt.name) - 1) {
	    PyErr_SetString(PyExc_TypeError, "name too long");
	    return -1;
	}
	strncpy(self->fmt.name, PyString_AsString(v), sizeof(self->fmt.name));
	self->fmt.namelen = size;
	self->fmt.name[size] = '\0';
	return 0;
    }
    return PyMember_Set((char *)self, CS_DATAFMT_memberlist, name, v);
}

static char CS_DATAFMTType__doc__[] = 
"";

PyTypeObject CS_DATAFMTType = {
    PyObject_HEAD_INIT(0)
    0,				/*ob_size*/
    "DataFmtType",		/*tp_name*/
    sizeof(CS_DATAFMTObj),	/*tp_basicsize*/
    0,				/*tp_itemsize*/
    /* methods */
    (destructor)CS_DATAFMT_dealloc,/*tp_dealloc*/
    (printfunc)0,		/*tp_print*/
    (getattrfunc)CS_DATAFMT_getattr, /*tp_getattr*/
    (setattrfunc)CS_DATAFMT_setattr, /*tp_setattr*/
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
    CS_DATAFMTType__doc__	/* Documentation string */
};
