#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2001 by Object Craft P/L, Melbourne, Australia.
#
# LICENCE - see LICENCE file distributed with this software for details.
#
# To use:
#       python setup.py install
#

"""Sybase module for Python

The Sybase module provides a Python interface to the Sybase relational
database system. The Sybase package supports all of the Python
Database API, version 2.0 with extensions.
"""

classifiers = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Programming Language :: Python
Topic :: Database
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: Microsoft :: Windows
Operating System :: Unix
"""

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages, Extension

import distutils
import os
import sys
import string
import re
from distutils.command.sdist import sdist

if sys.version_info < (2, 3):
    _setup = setup
    def setup(**kwargs):
        if kwargs.has_key("classifiers"):
            del kwargs["classifiers"]
        _setup(**kwargs)

doclines = __doc__.split("\n")

def api_exists(func, filename):
    try:
        text = open(filename).read()
    except:
        return 0
    if re.search(r'CS_PUBLIC|CS_RETCODE %s' % func, text):
        return 1

sybase = None
if os.environ.has_key('SYBASE'):
    sybase = os.environ['SYBASE']
    if os.environ.has_key('SYBASE_OCS'):
        ocs = os.environ['SYBASE_OCS']
        sybase = os.path.join(sybase, ocs)

have64bit = False
if sys.maxint > 2147483647:
    have64bit = True

if os.name == 'posix':                  # unix
    # Most people will define the location of their Sybase
    # installation in their environment.
    if sybase is None:
        # Not in environment - assume /opt/sybase
        sybase = '/opt/sybase'
        if not os.access(sybase, os.F_OK):
            sys.stderr.write(
                'Please define the Sybase installation directory in'
                ' the SYBASE environment variable.\n')
            sys.exit(1)
    # On Linux the Sybase tcl library is distributed as sybtcl
    syb_libs = []
    if os.uname()[0] == 'Linux':
        lib_names = ['blk', 'ct', 'cs', 'sybtcl', 'insck', 'comn', 'intl']
    elif os.uname()[0] == 'AIX':
        lib_names = ['blk', 'ct', 'cs', 'comn', 'tcl', 'intl', 'insck']
    else:
        lib_names = ['blk', 'ct', 'cs', 'tcl', 'comn', 'intl']
    # for Sybase 15.0
    lib_names += ['sybblk', 'sybct', 'sybcs', 'sybtcl', 'sybinsck', 'sybcomn', 'sybintl', 'sybunic']
    for name in lib_names:
        extensions = [('', 'a'), ('', 'so'), ('_r', 'a'), ('_r', 'so')]
        if have64bit and sys.platform not in ['osf1V5']:
            extensions = [('_r64', 'a'), ('_r64', 'so')]
        for (ext1, ext2) in extensions:
            lib_name = "%s%s" % (name, ext1)
            lib_path = os.path.join(sybase, 'lib', 'lib%s.%s' % (lib_name, ext2))
            if os.access(lib_path, os.R_OK):
                syb_libs.append(lib_name)
                break

elif os.name == 'nt':                   # win32
    # Not sure how the installation location is specified under NT
    if sybase is None:
        sybase = r'i:\sybase\sql11.5'
        if not os.access(sybase, os.F_OK):
            sys.stderr.write(
                'Please define the Sybase installation directory in'
                'the SYBASE environment variable.\n')
            sys.exit(1)
    syb_libs = ['libblk', 'libct', 'libcs']

else:                                   # unknown
    import sys
    sys.stderr.write(
        'Sorry, I do not know how to build on this platform.\n'
        '\n'
        'Please edit setup.py and add platform specific settings.  If you\n'
        'figure out how to get it working for your platform, please send\n'
        'mail to djc@object-craft.com.au so you can help other people.\n')
    sys.exit(1)

syb_incdir = '/usr/include/' #os.path.join(sybase, 'include')
syb_libdir = '/usr/lib/' #os.path.join(sybase, 'lib')
for dir in (syb_incdir, syb_libdir):
    if not os.access(dir, os.F_OK):
        sys.stderr.write('Directory %s does not exist - cannot build.\n' % dir)
        sys.exit(1)

extra_objects = None
runtime_library_dirs = None
try:
    if os.uname()[0] == 'SunOS':
        if have64bit:
            syb_libs.append('sybdb64')
        else:
            syb_libs.append('sybdb')
        syb_libs.remove('comn')
        extra_objects = [os.path.join(syb_libdir, 'libcomn.a')]
        runtime_library_dirs = [syb_libdir]
except:
    pass

syb_macros = [('WANT_BULKCOPY', None)]

if have64bit:
    syb_macros.append(('SYB_LP64', None))

# the C API to datetime only exists since python 2.4
if sys.version_info >= (2, 4):
    try:
        import datetime
    except ImportError:
        pass
    else:
        syb_macros.append(('HAVE_DATETIME', None))

try:
    from decimal import Decimal
except ImportError:
    pass
else:
    syb_macros.append(('HAVE_DECIMAL', None))

# distutils does not allow -D HAVE_FREETDS=60 so I have to find this
# argument myself and remove it from sys.argv and set the macro via
# the define_macros argument to the extension module.
for i in range(1, len(sys.argv)):
    # Find arguments like '-DHAVE_FREETDS=60' and variants
    parts = string.split(sys.argv[i], 'HAVE_FREETDS')
    if len(parts) == 1:
        continue
    prefix, suffix = parts[:2]
    # Ignore -DHAVE_FREETDS which does not set a value (=blah)
    if not suffix or suffix[0] != '=':
        continue
    # Remove this argument from sys.argv
    del sys.argv[i]
    # If -D was in previous argument then remove that as well
    if not prefix and sys.argv[i - 1] == '-D':
        del sys.argv[i - 1]
    # Now set the TDS level the other other way.
    syb_macros.append(('HAVE_FREETDS', suffix[1:]))
    if prefix:
        # Handle -D WANT_X,HAVE_FREETDS=60 case
        if prefix[-1] == ',':
            prefix = prefix[:-1]
        sys.argv[i:i] = [prefix]
    break

for api in ('blk_alloc', 'blk_describe', 'blk_drop', 'blk_rowxfer_mult',
            'blk_textxfer',):
    if api_exists(api, os.path.join(syb_incdir, 'bkpublic.h')):
        syb_macros.append(('HAVE_' + string.upper(api), None))
for api in ('ct_cursor', 'ct_data_info', 'ct_dynamic', 'ct_send_data',
            'ct_setparam',):
    if api_exists(api, os.path.join(syb_incdir, 'ctpublic.h')):
        syb_macros.append(('HAVE_' + string.upper(api), None))
for api in ('cs_calc', 'cs_cmp',):
    if api_exists(api, os.path.join(syb_incdir, 'cspublic.h')):
        syb_macros.append(('HAVE_' + string.upper(api), None))

class PreReleaseCheck:
    def __init__(self, distribution):
        self.distribution = distribution
        self.check_rev('doc/sybase.tex', r'^\\release{(.*)}')
        self.check_rev('Sybase.py', r'__version__ = \'(.*)\'')
        self.check_rev('sybasect.c', r'rev = PyString_FromString\("(.*)"\)')

    def _extract_rev(self, filename, pattern):
        regexp = re.compile(pattern)
        match = None
        revs = []
        line_num = 0
        f = open(filename)
        try:
            for line in f.readlines():
                line_num += 1
                match = regexp.search(line)
                if match:
                    revs.append((line_num, match.group(1)))
        finally:
            f.close()
        return revs

    def check_rev(self, filename, pattern):
        file_revs = self._extract_rev(filename, pattern)
        if not file_revs:
            sys.exit("Could not locate version in %s" % filename)
        line_num, file_rev = file_revs[0]
        for num, rev in file_revs[1:]:
            if rev != file_rev:
                sys.exit("%s:%d inconsistent version on line %d" % \
                         (filename, line_num, num))
        setup_rev = self.distribution.get_version()
        if file_rev != setup_rev:
            sys.exit("%s:%d version %s does not match setup.py version %s" % \
                     (filename, line_num, file_rev, setup_rev))


class my_sdist(sdist):
    def run(self):
        PreReleaseCheck(self.distribution)
        self.announce("Pre-release checks pass!")
        sdist.run(self)

setup(name="python-sybase",
      version="0.39",
      maintainer=u"Sebastien Sable",
      maintainer_email="sable@users.sourceforge.net",
      description=doclines[0],
      url="http://python-sybase.sourceforge.net/",
      license="http://www.opensource.org/licenses/bsd-license.html",
      platforms = ["any"],
      classifiers = filter(None, classifiers.split("\n")),
      long_description = "\n".join(doclines[2:]),
      py_modules=['Sybase'],
      include_dirs=[syb_incdir],
      ext_modules=[
          Extension('sybasect',
                    ['blk.c', 'databuf.c', 'cmd.c', 'conn.c', 'ctx.c',
                     'datafmt.c', 'iodesc.c', 'locale.c', 'msgs.c',
                     'numeric.c', 'money.c', 'datetime.c', 'date.c',
                     'sybasect.c'],
                    define_macros=syb_macros,
                    libraries=syb_libs,
                    library_dirs=[syb_libdir],
                    runtime_library_dirs=runtime_library_dirs,
                    extra_objects=extra_objects
                    )
          ],
      cmdclass={'sdist': my_sdist},
      # test_suite = 'nose.collector' # easy_setup only
      )

