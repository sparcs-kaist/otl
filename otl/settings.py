# Django settings for otl project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('OTL-Project Team', 'otl@server.daybreaker.info'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'test.db'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
TEST_DATABASE_CHARSET = 'utf8'

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
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '9f-56+0#6j8e_pqc=wmlp_58$3q@s6bwe()(s4fb_6^3=x+8fo'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)
TEMPLATE_CONTEXT_PROCESSORS = (
	'django.core.context_processors.auth',
	'django.core.context_processors.debug',
	'django.core.context_processors.i18n',
	'django.core.context_processors.media',
	'otl.utils.context_processors.globaltime',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'otl.utils.middleware.CachedAuthMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
)

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
    'otl.apps.timetable',
    'otl.apps.calendar',
    'otl.apps.groups',
    'otl.apps.favorites',
    'otl.apps.appointment',
    'otl.apps.accounts',
    'otl.utils',
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
NEXT_SEMESTER = 1

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

try:
	from otl.settings_local import *
except ImportError:
	pass
