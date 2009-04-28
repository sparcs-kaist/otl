# Used by all of the example programs.
#
import string
from sybasect import *

class Error(Exception):
    pass

def get_client_msgs(err, func):
    status, num_msgs = func(CS_STATUS, CS_CLIENTMSG_TYPE)
    if status != CS_SUCCEED:
        return
    for i in range(num_msgs):
        status, msg = func(CS_GET, CS_CLIENTMSG_TYPE, i + 1)
        if status != CS_SUCCEED:
            continue
        err.append('layer (%s), origin (%s)' \
                   % (CS_LAYER(msg.msgnumber), CS_ORIGIN(msg.msgnumber)))
        err.append('text:')
        err.append(msg.msgstring)
        if msg.osstring:
            err.append('OS error: %s' % msg.osstring)

def get_server_msgs(err, func):
    status, num_msgs = func(CS_STATUS, CS_SERVERMSG_TYPE)
    if status != CS_SUCCEED:
        return
    for i in range(num_msgs):
        status, msg = func(CS_GET, CS_SERVERMSG_TYPE, i + 1)
        if status != CS_SUCCEED:
            continue
        err.append('number (%s), severity (%s)' \
                   % (msg.msgnumber, msg.severity))
        err.append('state (%s), line (%s)' % (msg.state, msg.line))
        err.append('text:')
        err.append(msg.text)

class SyError:
    def __init__(self, msg):
        self.err = [msg]

    def __str__(self):
        return string.join(self.err, '\n')

class CTError(SyError):
    def __init__(self, conn, msg):
        SyError.__init__(self, msg)
        get_server_msgs(self.err, conn.ct_diag)
        get_client_msgs(self.err, conn.ct_diag)
        conn.ct_diag(CS_CLEAR, CS_ALLMSG_TYPE)

class CSError(SyError):
    def __init__(self, ctx, msg):
        SyError.__init__(self, msg)
        get_client_msgs(self.err, ctx.cs_diag)
        ctx.cs_diag(CS_CLEAR, CS_CLIENTMSG_TYPE)

EX_USERNAME = "sa"
EX_PASSWORD = ""
EX_CTLIB_VERSION = CS_VERSION_110
EX_BLK_VERSION = BLK_VERSION_110
