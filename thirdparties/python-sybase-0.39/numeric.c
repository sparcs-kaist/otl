/******************************************************************

 Copyright 2001 by Object Craft P/L, Melbourne, Australia.

 LICENCE - see LICENCE file distributed with this software for details.

******************************************************************/

#include "sybasect.h"

#define maxv(a,b) ((a) > (b) ? (a) : (b))

PyTypeObject NumericType;

static struct PyMethodDef Numeric_methods[] = {
    { NULL }			/* sentinel */
};

int numeric_as_string(PyObject *obj, char *text)
{
    CS_DATAFMT numeric_fmt;
    CS_DATAFMT char_fmt;
    CS_CONTEXT *ctx;
    CS_INT char_len;

    numeric_datafmt(&numeric_fmt, CS_SRC_VALUE, CS_SRC_VALUE);
    char_datafmt(&char_fmt);

    ctx = global_ctx();
    if (ctx == NULL)
	return CS_FAIL;
    return cs_convert(ctx, &numeric_fmt, &((NumericObj*)obj)->num,
		      &char_fmt, text, &char_len);
}

NumericObj *numeric_alloc(CS_NUMERIC *num)
{
    NumericObj *self;

    self = PyObject_NEW(NumericObj, &NumericType);
    if (self == NULL)
	return NULL;

    SY_LEAK_REG(self);
    memcpy(&self->num, num, sizeof(self->num));
    return self;
}

static int numeric_from_int(CS_NUMERIC *num, int precision, int scale, CS_INT value)
{
    CS_DATAFMT int_fmt;
    CS_DATAFMT numeric_fmt;
    CS_CONTEXT *ctx;
    CS_INT numeric_len;
    CS_RETCODE conv_result;

    int_datafmt(&int_fmt);
    if (precision < 0)
	precision = 16;
    if (scale < 0)
	scale = 0;
    numeric_datafmt(&numeric_fmt, precision, scale);

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return 0;
    conv_result = cs_convert(ctx, &int_fmt, &value,
			     &numeric_fmt, num, &numeric_len);
    if (PyErr_Occurred())
	return 0;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "numeric from int conversion failed");
	return 0;
    }
    return 1;
}

static int numeric_from_long(CS_NUMERIC *num, int precision, int scale, PyObject *obj)
{
    CS_DATAFMT char_fmt;
    CS_DATAFMT numeric_fmt;
    CS_CONTEXT *ctx;
    CS_INT numeric_len;
    CS_RETCODE conv_result;
    PyObject *strobj = PyObject_Str(obj);
    char *str;
    int num_digits;

    if (strobj == NULL)
	return 0;
    str = PyString_AsString(strobj);
    num_digits = strlen(str);
    if (str[num_digits - 1] == 'L')
	num_digits--;
    char_datafmt(&char_fmt);
    char_fmt.maxlength = num_digits;

    if (precision < 0)
	precision = num_digits;
    if (precision > CS_MAX_PREC)
	precision = CS_MAX_PREC;
    if (scale < 0)
	scale = 0;
    numeric_datafmt(&numeric_fmt, precision, scale);

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return 0;
    conv_result = cs_convert(ctx, &char_fmt, str,
			     &numeric_fmt, num, &numeric_len);
    Py_DECREF(strobj);
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "numeric from long conversion failed");
	return 0;
    }
    if (PyErr_Occurred())
	return 0;
    return 1;
}

static int numeric_from_float(CS_NUMERIC *num, int precision, int scale, CS_FLOAT value)
{
    CS_DATAFMT float_fmt;
    CS_DATAFMT numeric_fmt;
    CS_CONTEXT *ctx;
    CS_INT numeric_len;
    CS_RETCODE conv_result;

    float_datafmt(&float_fmt);
    if (precision < 0)
	precision = CS_MAX_PREC;
    if (scale < 0)
	scale = 12;
    numeric_datafmt(&numeric_fmt, precision, scale);

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return 0;
    conv_result = cs_convert(ctx, &float_fmt, &value,
			     &numeric_fmt, num, &numeric_len);
    if (PyErr_Occurred())
	return 0;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "numeric from float conversion failed");
	return 0;
    }
    return 1;
}

static int numeric_from_string(CS_NUMERIC *num, int precision, int scale, char *str)
{
    CS_DATAFMT char_fmt;
    CS_DATAFMT numeric_fmt;
    CS_CONTEXT *ctx;
    CS_INT numeric_len;
    char *dp, *ep;
    int len = strlen(str);
    CS_RETCODE conv_result;

    char_datafmt(&char_fmt);
    char_fmt.maxlength = len;
    if (scale < 0 || precision < 0) {
      int integers = len;
      int decimals = 0;
      int exponent = 0;

      if (str[0] == '-')
	integers -= 1;

      /* decimal notation */
      dp = strchr(str, '.');
      if (dp) {
	decimals = len - (dp - str) - 1;
	integers -= decimals + 1;
      }

      /* engineer notation */
      ep = strchr(str, 'e');
      if (!ep) ep = strchr(str, 'E');
      if (ep) {
	if (!decimals)
	  integers -= len - (ep - str);
	else
	  decimals -= len - (ep - str);
	exponent = atoi(ep+1);
	integers += exponent;
	if (integers < 0)
	  integers = 0;
	decimals -= exponent;
	if (decimals < 0)
	  decimals = 0;
      }

      if (precision < 0) {
	precision = integers + decimals;
	if (precision > CS_MAX_PREC) {
	  precision = CS_MAX_PREC;
	}
      }

      if (integers > precision) {
	PyErr_SetString(PyExc_ValueError, "numeric from string conversion failed - number too big");
	return 0;
      }

      if (integers + decimals > precision) {
	/* TODO: warning truncating */
	decimals = precision - integers;
      }

      if (scale < 0) {
	if (decimals > CS_MAX_SCALE)
	  decimals = CS_MAX_SCALE;
	scale = decimals;
      }
    }

    if (scale > precision) {
      PyErr_SetString(PyExc_ValueError, "numeric from string conversion failed - scale > precision");
      return 0;
    }
    if (scale > CS_MAX_SCALE) {
      PyErr_SetString(PyExc_ValueError, "numeric from string conversion failed - scale > CS_MAX_SCALE");
      return 0;
    }
    if (precision > CS_MAX_PREC) {
      PyErr_SetString(PyExc_ValueError, "numeric from string conversion failed - precision > CS_MAX_PREC");
      return 0;
    }

    numeric_datafmt(&numeric_fmt, precision, scale);

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return 0;
    conv_result = cs_convert(ctx, &char_fmt, str,
			     &numeric_fmt, num, &numeric_len);
    if (PyErr_Occurred())
	return 0;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "numeric from string conversion failed");
	return 0;
    }
    return 1;
}

static int numeric_from_numeric(CS_NUMERIC *num, int precision, int scale, CS_NUMERIC *value)
{
    CS_DATAFMT src_numeric_fmt;
    CS_DATAFMT numeric_fmt;
    CS_CONTEXT *ctx;
    CS_INT numeric_len;
    CS_RETCODE conv_result;

    if ((precision < 0 || precision == value->precision)
	&& (scale < 0 || scale == value->scale)) {
	*num = *value;
	return 1;
    }
    numeric_datafmt(&src_numeric_fmt, CS_SRC_VALUE, CS_SRC_VALUE);
    if (precision < 0)
	precision = value->precision;
    if (scale < 0)
	scale = value->scale;
    numeric_datafmt(&numeric_fmt, precision, scale);

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return 0;
    conv_result = cs_convert(ctx, &src_numeric_fmt, value,
			     &numeric_fmt, num, &numeric_len);
    if (PyErr_Occurred())
	return 0;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "numeric conversion failed");
	return 0;
    }
    return 1;
}

int numeric_from_value(CS_NUMERIC *num, int precision, int scale, PyObject *obj)
{
    PyObject *str;
    int res;

    if (PyInt_Check(obj))
	return numeric_from_int(num, precision, scale, PyInt_AsLong(obj));
    else if (PyLong_Check(obj))
	return numeric_from_long(num, precision, scale, obj);
    else if (PyFloat_Check(obj))
	return numeric_from_float(num, precision, scale, PyFloat_AsDouble(obj));
    else if (PyString_Check(obj))
	return numeric_from_string(num, precision, scale, PyString_AsString(obj));
    else if (Numeric_Check(obj))
	return numeric_from_numeric(num, precision, scale,
				    &((NumericObj*)obj)->num);
    else if (pydecimal_check(obj)) {
	str = PyObject_Str(obj);
	res = numeric_from_string(num, precision, scale, PyString_AsString(str));
	Py_DECREF(str);
	return res;
    }						   
    PyErr_SetString(PyExc_TypeError, "could not convert to Numeric");
    return 0;
}

NumericObj *Numeric_FromInt(PyObject *obj, int precision, int scale)
{
    CS_NUMERIC num;

    if (numeric_from_int(&num, precision, scale, PyInt_AsLong(obj)))
	return numeric_alloc(&num);
    return NULL;
}

NumericObj *Numeric_FromLong(PyObject *obj, int precision, int scale)
{
    CS_NUMERIC num;

    if (numeric_from_long(&num, precision, scale, obj))
	return numeric_alloc(&num);
    return NULL;
}

NumericObj *Numeric_FromString(PyObject *obj, int precision, int scale)
{
    CS_NUMERIC num;

    if (numeric_from_string(&num, precision, scale, PyString_AsString(obj)))
	return numeric_alloc(&num);
    return NULL;
}

NumericObj *Numeric_FromFloat(PyObject *obj, int precision, int scale)
{
    CS_NUMERIC num;

    if (numeric_from_float(&num, precision, scale, PyFloat_AsDouble(obj)))
	return numeric_alloc(&num);
    return NULL;
}

NumericObj *Numeric_FromNumeric(PyObject *obj, int precision, int scale)
{
    CS_NUMERIC num;

    if ((precision < 0 || precision == ((NumericObj*)obj)->num.precision)
	&& (scale < 0 || scale == ((NumericObj*)obj)->num.scale)) {
	Py_INCREF(obj);
	return (NumericObj*)obj;
    }
    if (numeric_from_numeric(&num, precision, scale,
			     &((NumericObj*)obj)->num))
	return numeric_alloc(&num);
    return NULL;
}

static void Numeric_dealloc(NumericObj *self)
{
    SY_LEAK_UNREG(self);
    PyObject_DEL(self);
}

#ifdef HAVE_CS_CMP
static int Numeric_compare(NumericObj *v, NumericObj *w)
{
    CS_INT result;
    CS_CONTEXT *ctx;
    CS_RETCODE cmp_result;

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return 0;
    cmp_result = cs_cmp(ctx, CS_NUMERIC_TYPE,
			&v->num, &w->num, &result);
    if (PyErr_Occurred())
	return 0;
    if (cmp_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "compare failed");
	return 0;
    }

    return result;
}
#endif

static PyObject *Numeric_repr(NumericObj *self)
{
    char text[NUMERIC_LEN];
    CS_RETCODE conv_result;

    /* PyErr_Clear(); */
    conv_result = numeric_as_string((PyObject*)self, text);
    if (PyErr_Occurred())
	return NULL;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "numeric to string conversion failed");
	return NULL;
    }

    return PyString_FromString(text);
}

static PyObject *Numeric_long(NumericObj *v);

/* Implement a hash function such that:
 * hash(100) == hash(Sybase.numeric(100))
 * hash(100200300400500L) == hash(Sybase.numeric(100200300400500L))
 */
static long Numeric_hash(NumericObj *self)
{
    long hash;
    CS_DATAFMT numeric_fmt;
    CS_DATAFMT int_fmt;
    CS_CONTEXT *ctx;
    CS_INT int_value;
    CS_INT int_len;
    CS_RETCODE conv_result;
    PyObject *long_value;

    /* Only use own hash for numbers with decimal places
     */
    if (self->num.scale > 0) {
	int i;

	hash = 0;
	for (i = 0; i < sizeof(self->num.array); i++)
	    hash = hash * 31 + self->num.array[i];
	return (hash == -1) ? -2 : hash;
    }
    /* Try as int
     */
    numeric_datafmt(&numeric_fmt, CS_SRC_VALUE, CS_SRC_VALUE);
    int_datafmt(&int_fmt);

    ctx = global_ctx();
    if (ctx == NULL)
	return -1;
    conv_result = cs_convert(ctx, &numeric_fmt, &self->num,
			     &int_fmt, &int_value, &int_len);
    if (conv_result == CS_SUCCEED)
	return (int_value == -1) ? -2 : int_value;
    /* PyErr_Clear(); */
    /* XXX clear_cs_messages(); */
    /* Try as long
     */
    long_value = Numeric_long(self);
    if (long_value != NULL) {
	hash = PyObject_Hash(long_value);
	Py_DECREF(long_value);
	return hash;
    }
    return -1;
}

#ifdef HAVE_CS_CALC
static NumericObj *numeric_minusone(void)
{
    static NumericObj *minusone;

    if (minusone == NULL) {
	CS_NUMERIC num;

	if (numeric_from_int(&num, -1, -1, -1))
	    minusone = numeric_alloc(&num);
	else
	    return NULL;
    }
    return minusone;
}

static NumericObj *numeric_zero(void)
{
    static NumericObj *zero;

    if (zero == NULL) {
	CS_NUMERIC num;

	if (numeric_from_int(&num, -1, -1, 0))
	    zero = numeric_alloc(&num);
	else
	    return NULL;
    }
    return zero;
}

/* Code to access Numeric objects as numbers */
static PyObject *Numeric_add(NumericObj *v, NumericObj *w)
{
    CS_NUMERIC result;
    CS_CONTEXT *ctx;
    CS_RETCODE calc_result;

    result.precision = maxv(v->num.precision, w->num.precision) + 1;
    if (result.precision > CS_MAX_PREC)
	result.precision = CS_MAX_PREC;
    result.scale = maxv(v->num.scale, w->num.scale);

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return NULL;
    calc_result = cs_calc(ctx, CS_ADD, CS_NUMERIC_TYPE,
			  &v->num, &w->num, &result);
    if (PyErr_Occurred())
	return NULL;
    if (calc_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "numeric add failed");
	return NULL;
    }

    return (PyObject*)numeric_alloc(&result);
}

static PyObject *Numeric_sub(NumericObj *v, NumericObj *w)
{
    CS_NUMERIC result;
    CS_CONTEXT *ctx;
    CS_RETCODE calc_result;

    result.precision = maxv(v->num.precision, w->num.precision) + 1;
    if (result.precision > CS_MAX_PREC)
	result.precision = CS_MAX_PREC;
    result.scale = maxv(v->num.scale, w->num.scale);

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return NULL;
    calc_result = cs_calc(ctx, CS_SUB, CS_NUMERIC_TYPE,
			  &v->num, &w->num, &result);
    if (PyErr_Occurred())
	return NULL;
    if (calc_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "numeric sub failed");
	return NULL;
    }

    return (PyObject*)numeric_alloc(&result);
}

static PyObject *Numeric_mul(NumericObj *v, NumericObj *w)
{
    CS_NUMERIC result;
    CS_CONTEXT *ctx;
    CS_RETCODE calc_result;

    result.precision = v->num.precision + w->num.precision;
    if (result.precision > CS_MAX_PREC)
	result.precision = CS_MAX_PREC;
    result.scale = v->num.scale + w->num.scale;
    if (result.scale > CS_MAX_SCALE)
	result.scale = CS_MAX_SCALE;

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return NULL;
    calc_result = cs_calc(ctx, CS_MULT, CS_NUMERIC_TYPE,
			  &v->num, &w->num, &result);
    if (PyErr_Occurred())
	return NULL;
    if (calc_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "numeric mul failed");
	return NULL;
    }

    return (PyObject*)numeric_alloc(&result);
}

static PyObject *Numeric_div(NumericObj *v, NumericObj *w)
{
    CS_NUMERIC result;
    CS_CONTEXT *ctx;
    CS_RETCODE calc_result;

    result.precision = v->num.precision + w->num.precision;
    if (result.precision > CS_MAX_PREC)
	result.precision = CS_MAX_PREC;
    result.scale = v->num.scale + w->num.scale;
    if (result.scale > CS_MAX_SCALE)
	result.scale = CS_MAX_SCALE;

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return NULL;
    calc_result = cs_calc(ctx, CS_DIV, CS_NUMERIC_TYPE,
			  &v->num, &w->num, &result);
    if (PyErr_Occurred())
	return NULL;
    if (calc_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "numeric div failed");
	return NULL;
    }

    return (PyObject*)numeric_alloc(&result);
}

static PyObject *Numeric_neg(NumericObj *v)
{
    return Numeric_mul(v, numeric_minusone());
}

static PyObject *Numeric_pos(NumericObj *v)
{
    Py_INCREF(v);
    return (PyObject*)v;
}

static PyObject *Numeric_abs(NumericObj *v)
{
    if (Numeric_compare(v, numeric_zero()) < 0)
	return Numeric_mul(v, numeric_minusone());
    if (PyErr_Occurred())
	return NULL;

    Py_INCREF(v);
    return (PyObject*)v;
}

static int Numeric_nonzero(NumericObj *v)
{
    return Numeric_compare(v, numeric_zero()) != 0;
}

static int Numeric_coerce(PyObject **pv, PyObject **pw)
{
    NumericObj *num = NULL;
    if (PyInt_Check(*pw))
	num = Numeric_FromInt(*pw, -1, -1);
    else if (PyLong_Check(*pw))
	num = Numeric_FromLong(*pw, -1, -1);
    else if (PyFloat_Check(*pw))
	num = Numeric_FromFloat(*pw, -1, -1);
    if (num) {
	*pw = (PyObject*)num;
	Py_INCREF(*pv);
	return 0;
    }
    return 1;
}
#endif

static PyObject *Numeric_int(NumericObj *v)
{
    CS_DATAFMT numeric_fmt;
    CS_DATAFMT int_fmt;
    CS_CONTEXT *ctx;
    CS_INT int_value;
    CS_INT int_len;
    CS_RETCODE conv_result;

    numeric_datafmt(&numeric_fmt, CS_SRC_VALUE, CS_SRC_VALUE);
    int_datafmt(&int_fmt);

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return NULL;
    conv_result = cs_convert(ctx, &numeric_fmt, &v->num,
			     &int_fmt, &int_value, &int_len);
    if (PyErr_Occurred())
	return NULL;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "int conversion failed");
	return NULL;
    }

    return PyInt_FromLong(int_value);
}

static PyObject *Numeric_long(NumericObj *v)
{
    char *end;
    char text[NUMERIC_LEN];
    CS_RETCODE conv_result;

    /* PyErr_Clear(); */
    conv_result = numeric_as_string((PyObject*)v, text);
    if (PyErr_Occurred())
	return NULL;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "numeric to string conversion failed");
	return NULL;
    }

    return PyLong_FromString(text, &end, 10);
}

static PyObject *Numeric_float(NumericObj *v)
{
    CS_DATAFMT numeric_fmt;
    CS_DATAFMT float_fmt;
    CS_CONTEXT *ctx;
    CS_FLOAT float_value;
    CS_INT float_len;
    CS_RETCODE conv_result;

    numeric_datafmt(&numeric_fmt, CS_SRC_VALUE, CS_SRC_VALUE);
    float_datafmt(&float_fmt);

    /* PyErr_Clear(); */
    ctx = global_ctx();
    if (ctx == NULL)
	return NULL;
    conv_result = cs_convert(ctx, &numeric_fmt, &v->num,
			     &float_fmt, &float_value, &float_len);
    if (PyErr_Occurred())
	return NULL;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "float conversion failed");
	return NULL;
    }

    return PyFloat_FromDouble(float_value);
}

static PyNumberMethods Numeric_as_number = {
#ifdef HAVE_CS_CALC
    (binaryfunc)Numeric_add,	/*nb_add*/
    (binaryfunc)Numeric_sub,	/*nb_subtract*/
    (binaryfunc)Numeric_mul,	/*nb_multiply*/
    (binaryfunc)Numeric_div,	/*nb_divide*/
#else
    0,				/*nb_add*/
    0,				/*nb_subtract*/
    0,				/*nb_multiply*/
    0,				/*nb_divide*/
#endif
    (binaryfunc)0,		/*nb_remainder*/
    (binaryfunc)0,		/*nb_divmod*/
    (ternaryfunc)0,		/*nb_power*/
#ifdef HAVE_CS_CALC
    (unaryfunc)Numeric_neg,	/*nb_negative*/
    (unaryfunc)Numeric_pos,	/*nb_positive*/
    (unaryfunc)Numeric_abs,	/*nb_absolute*/
    (inquiry)Numeric_nonzero,	/*nb_nonzero*/
#else
    0,				/*nb_negative*/
    0,				/*nb_positive*/
    0,				/*nb_absolute*/
    0,				/*nb_nonzero*/
#endif
    (unaryfunc)0,		/*nb_invert*/
    (binaryfunc)0,		/*nb_lshift*/
    (binaryfunc)0,		/*nb_rshift*/
    (binaryfunc)0,		/*nb_and*/
    (binaryfunc)0,		/*nb_xor*/
    (binaryfunc)0,		/*nb_or*/
#ifdef HAVE_CS_CALC
    (coercion)Numeric_coerce,	/*nb_coerce*/
#else
    0,				/*nb_coerce*/
#endif
    (unaryfunc)Numeric_int,	/*nb_int*/
    (unaryfunc)Numeric_long,	/*nb_long*/
    (unaryfunc)Numeric_float,	/*nb_float*/
    (unaryfunc)0,		/*nb_oct*/
    (unaryfunc)0,		/*nb_hex*/
};

#define OFF(x) offsetof(NumericObj, x)

static struct memberlist Numeric_memberlist[] = {
    { "precision", T_BYTE, OFF(num.precision), RO },
    { "scale",     T_BYTE, OFF(num.scale), RO },
    { NULL }			/* Sentinel */
};

static PyObject *Numeric_getattr(NumericObj *self, char *name)
{
    PyObject *rv;
	
    rv = PyMember_Get((char*)self, Numeric_memberlist, name);
    if (rv)
	return rv;
    PyErr_Clear();
    return Py_FindMethod(Numeric_methods, (PyObject *)self, name);
}

static int Numeric_setattr(NumericObj *self, char *name, PyObject *v)
{
    if (v == NULL) {
	PyErr_SetString(PyExc_AttributeError, "Cannot delete attribute");
	return -1;
    }
    return PyMember_Set((char*)self, Numeric_memberlist, name, v);
}

static char NumericType__doc__[] = 
"";

PyTypeObject NumericType = {
    PyObject_HEAD_INIT(0)
    0,				/*ob_size*/
    "NumericType",		/*tp_name*/
    sizeof(NumericObj),		/*tp_basicsize*/
    0,				/*tp_itemsize*/
    /* methods */
    (destructor)Numeric_dealloc,/*tp_dealloc*/
    (printfunc)0,		/*tp_print*/
    (getattrfunc)Numeric_getattr, /*tp_getattr*/
    (setattrfunc)Numeric_setattr, /*tp_setattr*/
#ifdef HAVE_CS_CMP
    (cmpfunc)Numeric_compare,	/*tp_compare*/
#else
    0,				/*tp_compare*/
#endif
    (reprfunc)Numeric_repr,	/*tp_repr*/
    &Numeric_as_number,		/*tp_as_number*/
    0,				/*tp_as_sequence*/
    0,				/*tp_as_mapping*/
    (hashfunc)Numeric_hash,	/*tp_hash*/
    (ternaryfunc)0,		/*tp_call*/
    (reprfunc)0,		/*tp_str*/

    /* Space for future expansion */
    0L,0L,0L,0L,
    NumericType__doc__		/* Documentation string */
};

char NumericType_new__doc__[] =
"numeric(num, precision = -1, scale = -1) -> num\n"
"\n"
"Create a Sybase numeric object.";

/* Implement the Sybase.numeric() method
 */
PyObject *NumericType_new(PyObject *module, PyObject *args)
{
    int precision, scale;
    PyObject *obj;
    CS_NUMERIC num;

    precision = -1;
    scale = -1;
    if (!PyArg_ParseTuple(args, "O|ii", &obj, &precision, &scale))
	return NULL;

    if (numeric_from_value(&num, precision, scale, obj))
	return (PyObject*)numeric_alloc(&num);
    else
	return NULL;
}

/* Used in unpickler
 */
static PyObject *numeric_constructor = NULL;

/* Register the numeric type with the copy_reg module.  This allows
 * Python to (un)pickle numeric objects.  The equivalent Python code
 * is this:
 *
 * def pickle_numeric(n):
 *     return numeric, (str(n), n.precision, n.scale)
 * 
 * copy_reg.pickle(type(numeric(1)), pickle_numeric, numeric)
 */
/* Numeric pickling function
 */
char pickle_numeric__doc__[] =
"pickle_numeric(n) -> numeric, (str(n), n.precision, n.scale)\n"
"\n"
"Used to pickle the numeric data type.";

PyObject *pickle_numeric(PyObject *module, PyObject *args)
{
    NumericObj *obj = NULL;
    PyObject *values = NULL,
	*tuple = NULL;
    char text[NUMERIC_LEN];
    CS_RETCODE conv_result;

    if (!PyArg_ParseTuple(args, "O!", &NumericType, &obj))
	goto error;

    /* PyErr_Clear(); */
    conv_result = numeric_as_string((PyObject*)obj, text);
    if (PyErr_Occurred())
	return NULL;
    if (conv_result != CS_SUCCEED) {
	PyErr_SetString(PyExc_TypeError, "numeric to string conversion failed");
	return NULL;
    }

    if ((values = Py_BuildValue("(sii)", text,
				obj->num.precision, obj->num.scale)) == NULL)
	goto error;
    tuple = Py_BuildValue("(OO)", numeric_constructor, values);

error:
    Py_XDECREF(values);
    return tuple;
}

/* Register Numeric type pickler
 */
int copy_reg_numeric(PyObject *dict)
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
    if ((numeric_constructor = PyDict_GetItemString(dict, "numeric")) == NULL)
	goto error;
    if ((pickler = PyDict_GetItemString(dict, "pickle_numeric")) == NULL)
	goto error;
    obj = PyObject_CallFunction(pickle_func, "OOO",
				&NumericType, pickler, numeric_constructor);

error:
    Py_XDECREF(obj);
    Py_XDECREF(pickle_func);
    Py_XDECREF(module);

    return (obj == NULL) ? -1 : 0;
}
