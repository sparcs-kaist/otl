/******************************************************************

 Copyright 2001 by Object Craft P/L, Melbourne, Australia.

 LICENCE - see LICENCE file distributed with this software for details.

******************************************************************/

#include "sybasect.h"

static int clientmsg_serial;

PyObject *clientmsg_alloc()
{
    CS_CLIENTMSGObj *self;

    self = PyObject_NEW(CS_CLIENTMSGObj, &CS_CLIENTMSGType);
    if (self == NULL)
	return NULL;

    SY_LEAK_REG(self);
    memset(&self->msg, 0, sizeof(self->msg));
    self->serial = clientmsg_serial++;

    return (PyObject*)self;
}

static void CS_CLIENTMSG_dealloc(CS_CLIENTMSGObj *self)
{
    SY_LEAK_UNREG(self);
    PyObject_DEL(self);
}

#define CLIENT_OFF(x) offsetof(CS_CLIENTMSG, x)

/* Adapted from Sybase cstypes.h */
#if defined (SYB_LP64) || defined (_AIX)
#define T_MSGNUM T_UINT
#else
#define T_MSGNUM T_LONG
#endif

static struct memberlist CS_CLIENTMSG_memberlist[] = {
    { "severity",  T_INT,    CLIENT_OFF(severity), RO },
    { "msgnumber", T_MSGNUM, CLIENT_OFF(msgnumber), RO },
    { "msgstring", T_STRING_INPLACE, CLIENT_OFF(msgstring), RO }, /* faked */
    { "osnumber",  T_INT,    CLIENT_OFF(osnumber), RO },
    { "osstring",  T_STRING_INPLACE, CLIENT_OFF(osstring), RO }, /* faked */
#ifndef HAVE_FREETDS
    { "status",    T_INT,    CLIENT_OFF(status), RO },
    { "sqlstate",  T_STRING_INPLACE, CLIENT_OFF(sqlstate), RO }, /* faked */
#endif
    { NULL }			/* Sentinel */
};

static PyObject *CS_CLIENTMSG_getattr(CS_CLIENTMSGObj *self, char *name)
{
    if (strcmp(name, "msgstring") == 0)
	return PyString_FromStringAndSize(self->msg.msgstring,
					  self->msg.msgstringlen);
    if (strcmp(name, "osstring") == 0)
	return PyString_FromStringAndSize(self->msg.osstring,
					  self->msg.osstringlen);
#ifndef HAVE_FREETDS
    if (strcmp(name, "sqlstate") == 0)
	return PyString_FromStringAndSize((char *)self->msg.sqlstate,
					  self->msg.sqlstatelen);
#endif
    return PyMember_Get((char *)&self->msg, CS_CLIENTMSG_memberlist, name);
}

static int CS_CLIENTMSG_setattr(CS_CLIENTMSGObj *self, char *name, PyObject *v)
{
    if (v == NULL) {
	PyErr_SetString(PyExc_AttributeError, "Cannot delete attribute");
	return -1;
    }
    return PyMember_Set((char *)&self->msg, CS_CLIENTMSG_memberlist, name, v);
}

static char CS_CLIENTMSGType__doc__[] = 
"";

PyTypeObject CS_CLIENTMSGType = {
    PyObject_HEAD_INIT(0)
    0,				/*ob_size*/
    "ClientMsgType",		/*tp_name*/
    sizeof(CS_CLIENTMSGObj),	/*tp_basicsize*/
    0,				/*tp_itemsize*/
    /* methods */
    (destructor)CS_CLIENTMSG_dealloc,/*tp_dealloc*/
    (printfunc)0,		/*tp_print*/
    (getattrfunc)CS_CLIENTMSG_getattr, /*tp_getattr*/
    (setattrfunc)CS_CLIENTMSG_setattr, /*tp_setattr*/
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
    CS_CLIENTMSGType__doc__	/* Documentation string */
};

static int servermsg_serial;

PyObject *servermsg_alloc()
{
    CS_SERVERMSGObj *self;

    self = PyObject_NEW(CS_SERVERMSGObj, &CS_SERVERMSGType);
    if (self == NULL)
	return NULL;

    SY_LEAK_REG(self);
    memset(&self->msg, 0, sizeof(self->msg));
    self->serial = servermsg_serial++;

    return (PyObject*)self;
}

static void CS_SERVERMSG_dealloc(CS_SERVERMSGObj *self)
{
    SY_LEAK_UNREG(self);
    PyObject_DEL(self);
}

#define SERV_OFF(x) offsetof(CS_SERVERMSG, x)

static struct memberlist CS_SERVERMSG_memberlist[] = {
    { "msgnumber", T_MSGNUM, SERV_OFF(msgnumber), RO },
    { "state",     T_INT,    SERV_OFF(state), RO },
    { "severity",  T_INT,    SERV_OFF(severity), RO },
    { "text",      T_STRING_INPLACE, SERV_OFF(text), RO }, /* faked */
    { "svrname",   T_STRING_INPLACE, SERV_OFF(svrname), RO }, /* faked */
    { "proc",      T_STRING_INPLACE, SERV_OFF(proc), RO }, /* faked */
    { "line",      T_INT,    SERV_OFF(line), RO },
    { "status",    T_INT,    SERV_OFF(status), RO },
#ifndef HAVE_FREETDS
    { "sqlstate",  T_STRING_INPLACE, SERV_OFF(sqlstate), RO }, /* faked */
#endif
    { NULL }			/* Sentinel */
};

static PyObject *CS_SERVERMSG_getattr(CS_SERVERMSGObj *self, char *name)
{
#ifndef HAVE_FREETDS
    if (strcmp(name, "text") == 0)
	return PyString_FromStringAndSize(self->msg.text,
					  self->msg.textlen);
#endif
    if (strcmp(name, "svrname") == 0)
	return PyString_FromStringAndSize(self->msg.svrname,
					  self->msg.svrnlen);
    if (strcmp(name, "proc") == 0)
	return PyString_FromStringAndSize(self->msg.proc,
					  self->msg.proclen);
#ifndef HAVE_FREETDS
    if (strcmp(name, "sqlstate") == 0)
	return PyString_FromStringAndSize((char *)self->msg.sqlstate,
					  self->msg.sqlstatelen);
#endif
    return PyMember_Get((char *)&self->msg, CS_SERVERMSG_memberlist, name);
}

static int CS_SERVERMSG_setattr(CS_SERVERMSGObj *self, char *name, PyObject *v)
{
    if (v == NULL) {
	PyErr_SetString(PyExc_AttributeError, "Cannot delete attribute");
	return -1;
    }
    return PyMember_Set((char *)&self->msg, CS_SERVERMSG_memberlist, name, v);
}

static char CS_SERVERMSGType__doc__[] = 
"";

PyTypeObject CS_SERVERMSGType = {
    PyObject_HEAD_INIT(0)
    0,				/*ob_size*/
    "ServerMsgType",		/*tp_name*/
    sizeof(CS_SERVERMSGObj),	/*tp_basicsize*/
    0,				/*tp_itemsize*/
    /* methods */
    (destructor)CS_SERVERMSG_dealloc,/*tp_dealloc*/
    (printfunc)0,		/*tp_print*/
    (getattrfunc)CS_SERVERMSG_getattr, /*tp_getattr*/
    (setattrfunc)CS_SERVERMSG_setattr, /*tp_setattr*/
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
    CS_SERVERMSGType__doc__	/* Documentation string */
};
