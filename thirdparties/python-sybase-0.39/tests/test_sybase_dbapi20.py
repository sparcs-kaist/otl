#!/usr/bin/env python

import os, sys
import unittest
from ConfigParser import SafeConfigParser

""" This test module requires a configuration file in ~/.sybase_dbapi20.conf
with the following format:

[Base 1]

server=myserver
database=mydatabase
user=myuser
password=mypasswordd

[Base 2]
...
"""

if os.environ.get("SYBASE", None) is not None:
    import sybase_dbapi20

    config = SafeConfigParser()
    try:
        config.read(os.path.expanduser(os.path.join("~", ".sybase_dbapi20.conf")))
    except IOError:
        pass
    else:
        curnb = 0
        for section in config.sections():
            server = config.get(section, "server")
            user = config.get(section, "user")
            passwd = config.get(section, "password")
            database = config.get(section, "database")
        
            exec("""class TestSybase%s(sybase_dbapi20.TestSybase):
            connect_args = (server, user, passwd, database)
            connect_kw_args = {'auto_commit': 0}""" % server)
        
            exec("""class TestSybase%sAutoCommit(sybase_dbapi20.TestSybase):
            connect_args = (server, user, passwd, database)
            connect_kw_args = {'auto_commit': 1}""" % server)

            exec("""class TestSybase%sAutoCommitForce(sybase_dbapi20.TestSybase):
            connect_args = (server, user, passwd, database)
            connect_kw_args = {'auto_commit': 1}
            force_commit = 1""" % server)

            exec("""class TestSybase%sNoLocking(sybase_dbapi20.TestSybase):
            connect_args = (server, user, passwd, database)
            connect_kw_args = {'auto_commit': 1, 'locking': 0}""" % server)

            curnb += 1

if __name__ == '__main__':
    unittest.main()
