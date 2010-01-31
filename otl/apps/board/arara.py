# -*- coding: utf-8
from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TTransportException
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.server import TServer
from otl.apps.board.arara_thrift import *
from django.core.cache import cache
from django.conf import settings

the_arara_server = None

HANDLER_MAPPING = [
    ('login_manager', LoginManager),
    ('member_manager', MemberManager),
    ('blacklist_manager', BlacklistManager),
    ('board_manager', BoardManager),
    ('read_status_manager', ReadStatusManager),
    ('article_manager', ArticleManager),
    ('messaging_manager', MessagingManager),
    ('notice_manager', NoticeManager),
    ('search_manager', SearchManager),
    ('file_manager', FileManager)
]

HANDLER_PORT = {
    'login_manager': 1,
    'member_manager': 2,
    'blacklist_manager': 3,
    'board_manager': 4,
    'read_status_manager': 5,
    'article_manager': 6,
    'messaging_manager': 7,
    'notice_manager': 8,
    'read_status_manager': 9,
    'search_manager': 10,
    'file_manager': 11,
}

SESSION_KEY = 'arara.sesskey'

class Server(object):
    def __init__(self):
        pass

    def _connect(self, name):
        host = settings.ARARA_HOST
        port = settings.ARARA_BASE_PORT + HANDLER_PORT[name]
        sock = TSocket.TSocket(settings.ARARA_HOST, settings.ARARA_BASE_PORT + HANDLER_PORT[name])
        sock.setTimeout(5000)
        transport = TTransport.TBufferedTransport(sock)
        protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
        client = dict(HANDLER_MAPPING)[name].Client(protocol)
        transport.open()
        return client
    
    def __getattr__(self, name):
        if name in dict(HANDLER_MAPPING):
            return self._connect(name)
        raise AttributeError()

def get_server():
    """Singleton 형태로 Server 오브젝트를 가져온다."""
    global the_arara_server
    if not the_arara_server:
        the_arara_server = Server()
    return the_arara_server

def get_session_key():
    return cache.get(SESSION_KEY)

def login():
    """캐시의 세션키를 검사하여 로그인이 되어 있지 않으면 로그인하고 세션키를 저장한다."""
    if cache.get(SESSION_KEY) != None:
        return True

    try:
        server = get_server()
        session_key = server.login_manager.login(settings.ARARA_USER, settings.ARARA_PASSWORD, '%s:%d' % (settings.ARARA_HOST, settings.ARARA_BASE_PORT))
        cache.set(SESSION_KEY, session_key, settings.ARARA_SESSION_TIMEOUT)
    except:
        return False

    return True
