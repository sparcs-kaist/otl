/******************************************************************

 Copyright 2001 by Object Craft P/L, Melbourne, Australia.

 LICENCE - see LICENCE file distributed with this software for details.

******************************************************************/

#include "sybasect.h"

static struct PyMethodDef CS_IODESC_methods[] = {
    { NULL }			/* sentinel */
};

static int iodesc_serial;

PyObject *iodesc_alloc(CS_IODESC *iodesc)
{
    CS_IODESCObj *self;

    self = PyObject_NEW(CS_IODESCObj, &CS_IODESCType);
    if (self == NULL)
	return NULL;

    SY_LEAK_REG(self);
    self->serial = iodesc_serial++;

    self->iodesc = *iodesc;
    return (PyObject*)self;
}

char iodesc_new__doc__[] =
"CS_IODESC() -> iodesc\n"
"\n"
"Allocate a new CS_IODESC object.";

PyObject *iodesc_new(PyObject *module, PyObject *args)
{
    CS_IODESCObj *self;

    if (!PyArg_ParseTuple(args, ""))
	return NULL;

    self = PyObject_NEW(CS_IODESCObj, &CS_IODESCType);
    if (self == NULL)
	return NULL;

    SY_LEAK_REG(self);
    memset(&self->iodesc, 0, sizeof(self->iodesc));
    self->serial = iodesc_serial++;

    return (PyObject*)self;
}

static void CS_IODESC_dealloc(CS_IODESCObj *self)
{
    SY_LEAK_UNREG(self);
    PyObject_DEL(self);
}

/* Code to access structure members by accessing attributes */

#define OFF(x) offsetof(CS_IODESCObj, x)

static struct memberlist CS_IODESC_memberlist[] = {
    { "iotype",        T_INT,    OFF(iodesc.iotype) },
    { "datatype",      T_INT,    OFF(iodesc.datatype) },
    { "usertype",      T_INT,    OFF(iodesc.usertype) },
    { "total_txtlen",  T_INT,    OFF(iodesc.total_txtlen) },
    { "offset",        T_INT,    OFF(iodesc.offset) },
    { "log_on_update", T_INT,    OFF(iodesc.log_on_update) },
    { "name",          T_STRING_INPLACE, OFF(iodesc.name) }, /* faked */
    { "timestamp",     T_STRING_INPLACE, OFF(iodesc.timestamp) }, /* faked */
    { "textptr",       T_STRING_INPLACE, OFF(iodesc.textptr) }, /* faked */
    { NULL }			/* Sentinel */
};

static PyObject *CS_IODESC_getattr(CS_IODESCObj *self, char *name)
{
    PyObject *rv;

    if (strcmp(name, "name") == 0)
	return PyString_FromStringAndSize(self->iodesc.name,
					  self->iodesc.namelen);
    if (strcmp(name, "timestamp") == 0)
        return PyString_FromStringAndSize((char *)self->iodesc.timestamp,
					  self->iodesc.timestamplen);
    if (strcmp(name, "textptr") == 0)
	return PyString_FromStringAndSize((char *)self->iodesc.textptr,
					  self->iodesc.textptrlen);

    rv = PyMember_Get((char *)self, CS_IODESC_memberlist, name);
    if (rv)
	return rv;
    PyErr_Clear();
    return Py_FindMethod(CS_IODESC_methods, (PyObject *)self, name);
}

static int CS_IODESC_setattr(CS_IODESCObj *self, char *name, PyObject *v)
{
    void *ptr = NULL;
    CS_INT *len_ptr = NULL;
    int max_len = 0;

    if (v == NULL) {
	PyErr_SetString(PyExc_AttributeError, "Cannot delete attribute");
	return -1;
    }
    if (strcmp(name, "name") == 0) {
	ptr = self->iodesc.name;
	len_ptr = &self->iodesc.namelen;
	max_len = sizeof(self->iodesc.name);
    } else if (strcmp(name, "timestamp") == 0) {
	ptr = self->iodesc.timestamp;
	len_ptr = &self->iodesc.timestamplen;
	max_len = sizeof(self->iodesc.timestamp);
    } else if (strcmp(name, "textptr") == 0) {
	ptr = self->iodesc.textptr;
	len_ptr = &self->iodesc.textptrlen;
	max_len = sizeof(self->iodesc.textptr);
    }
    if (ptr != NULL) {
	int size;

	if (!PyString_Check(v)) {
	    PyErr_BadArgument();
	    return -1;
	}
	size = PyString_Size(v);
	if (size > max_len) {
	    PyErr_SetString(PyExc_TypeError, "too long");
	    return -1;
	}
	memmove(ptr, PyString_AsString(v), size);
	*len_ptr = size;
	return 0;
    }
    return PyMember_Set((char *)self, CS_IODESC_memberlist, name, v);
}

static char CS_IODESCType__doc__[] = 
"";

PyTypeObject CS_IODESCType = {
    PyObject_HEAD_INIT(0)
    0,				/*ob_size*/
    "IODescType",		/*tp_name*/
    sizeof(CS_IODESCObj),	/*tp_basicsize*/
    0,				/*tp_itemsize*/
    /* methods */
    (destructor)CS_IODESC_dealloc,/*tp_dealloc*/
    (printfunc)0,		/*tp_print*/
    (getattrfunc)CS_IODESC_getattr, /*tp_getattr*/
    (setattrfunc)CS_IODESC_setattr, /*tp_setattr*/
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
    CS_IODESCType__doc__	/* Documentation string */
};
