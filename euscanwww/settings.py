# Django settings for euscanwww project.

import os.path

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('admin', 'admin@example.com'),
)

MANAGERS = ADMINS

"""
# MySQL Example:
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'euscan',
        'USER': 'euscan',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
        'OPTIONS': {
            'init_command': 'SET storage_engine=INNODB',
         }
    },

# PostGreSQL Example:
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'euscan',
        'USER': 'euscan',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    },
"""

EUSCAN_ROOT = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(EUSCAN_ROOT, 'euscan.db')
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(EUSCAN_ROOT, 'euscan.cache'),
    }
}

RRD_ROOT = os.path.join(EUSCAN_ROOT, 'rrd')

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(EUSCAN_ROOT, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '00000000000000000000000000000000000000000000000000'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

CACHE_MIDDLEWARE_SECONDS=3600
CACHE_MIDDLEWARE_ANONYMOUS_ONLY=True

ROOT_URLCONF = 'euscanwww.urls'

FORCE_SCRIPT_NAME=""

TEMPLATE_DIRS = (
    os.path.join(EUSCAN_ROOT, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'south',
    'euscan',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

try:
    from local_settings import *
except ImportError, ex:
    import sys
    sys.stderr.write(\
            ("settings.py: error importing local settings file:\n" + \
            "\t%s\n" + \
            "Do you have a local_settings.py module?\n") % str(ex))
    raise
