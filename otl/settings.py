# Django settings for otl project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('OTL-Project Team', 'otlsysop@sparcs.kaist.ac.kr'),
)

MANAGERS = ADMINS

DATABASES = {
        'default':{
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'test.db',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
}

#DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#DATABASE_NAME = 'test.db'             # Or path to database file if using sqlite3.
#DATABASE_USER = ''             # Not used with sqlite3.
#DATABASE_PASSWORD = ''         # Not used with sqlite3.
#DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
#DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
#TEST_DATABASE_CHARSET = 'utf8'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Seoul'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ko-KR'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

import os.path
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '9f-56+0#6j8e_pqc=wmlp_58$3q@s6bwe()(s4fb_6^3=x+8fo'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#    'django.template.loaders.filesystem.load_template_source',
#    'django.template.loaders.app_directories.load_template_source',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
#   'django.core.context_processors.auth', //Version 1.3
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'otl.utils.context_processors.globaltime',
    'otl.utils.context_processors.myfavorites',
    'otl.utils.context_processors.favorites',
    'otl.utils.context_processors.taken_lecture_list',
)

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'otl.utils.middleware.CachedAuthMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    ]
if DEBUG:
    try:
        import firepy
        MIDDLEWARE_CLASSES += ['firepy.django.middleware.FirePHPMiddleware']
    except ImportError:
        pass

ROOT_URLCONF = 'otl.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'templates')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'otl',
    'otl.utils',
    'otl.apps.dictionary',
    'otl.apps.timetable',
    'otl.apps.calendar',
    'otl.apps.groups',
    'otl.apps.favorites',
    'otl.apps.appointment',
    'otl.apps.accounts',
    'otl.apps.main',
    'django_extensions',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'otl.apps.accounts.backends.KAISTSSOBackend',
)
AUTH_PROFILE_MODULE = 'apps.accounts.userprofile'
LOGIN_URL = '/login/'

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 2*3600

# Should be overriden at settings_local.py
SERVICE_STATUS = 'released'

from datetime import date
CURRENT_YEAR = 2009
CURRENT_SEMESTER = 1
NEXT_YEAR = 2009
NEXT_SEMESTER = 3
START_YEAR = 2009
START_SEMESTER = 1
SEMESTER_RANGES = {
    (2009,1): (date(2009,2,2), date(2009,5,22)),
    (2009,3): (date(2009,9,1), date(2009,12,21)),
}
EXAM_PERIODS = {
    (2009,1): ((date(2009,3,23), date(2009,3,27)), (date(2009,5,18), date(2009,5,22))),
    (2009,3): ((date(2009,10,20), date(2009,10,26)), (date(2009,12,15), date(2009,12,21))),
}

NUMBER_OF_TABS = 3

SCHOLARDB_HOST = ''
SCHOLARDB_USER = ''
SCHOLARDB_PASSWORD = ''
SCHOLARDB_NAME = ''

MOODLEDB_HOST = 'moodle.kaist.ac.kr'
MOODLEDB_USER = ''
MOODLEDB_PASSWORD = ''
MOODLEDB_NAME = ''

ARARA_HOST = ''
ARARA_BASE_PORT = 0
ARARA_USER = ''
ARARA_PASSWORD = ''
ARARA_SESSION_TIMEOUT = 3600

CACHE_BACKEND = 'dummy:///'

PORTAL_SSO_ADMIN_ID = ''
PORTAL_SSO_ADMIN_PASSWORD = ''
PORTAL_SSO_TOKEN = ''
PORTAL_SSO_WSDL_ADDRESS = 'https://ksso.kaist.ac.kr/kstsso/services/simpleAuthSrv?wsdl'

COMMENT_NUM = 10

try:
    from otl.settings_local import *
except ImportError:
    pass
