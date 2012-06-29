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

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# euscan specific config
EUSCAN_ROOT = SITE_ROOT
RRD_ROOT = os.path.join(EUSCAN_ROOT, 'var', 'rrd')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(EUSCAN_ROOT, 'var', 'db', 'euscan.db')
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(EUSCAN_ROOT, 'var', 'cache'),
    }
}

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

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(SITE_ROOT, 'var', 'uploads')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(SITE_ROOT, 'htdocs'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    # Cache middleware
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # Disable Csrf for now
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

CACHE_MIDDLEWARE_SECONDS = 3600
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

ROOT_URLCONF = 'euscanwww.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'euscanwww.wsgi.application'

FORCE_SCRIPT_NAME = ""

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

INSTALLED_APPS = (
    'euscanwww',
    'djeuscan',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'south',
    'djcelery',
    'registration',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'djeuscan': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

# django-registration
ACCOUNT_ACTIVATION_DAYS = 7
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# djeuscan tasks
PORTAGE_ROOT = "/usr/portage/"
PORTAGE_CONFIGROOT = PORTAGE_ROOT
LAYMAN_CONFIG = "/etc/layman/layman.cfg"
EMERGE_REGEN_JOBS = 4

# Celery config
import djcelery
djcelery.setup_loader()
BROKER_URL = "amqp://guest:guest@localhost:5672//"
CELERY_RESULT_BACKEND = "amqp"
BROKER_CONNECTION_TIMEOUT = 3600
CELERYD_CONCURRENCY = 4

TASKS_CONCURRENTLY = 4
TASKS_SUBTASK_PACKAGES = 32

# LDAP authentication
# TODO: Test data - change me!
AUTH_LDAP_SERVER_URI = "ldap://localhost"
AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=users,dc=my-domain,dc=com"
AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

try:
    from local_settings import *
except ImportError, ex:
    import sys
    sys.stderr.write(
        "settings.py: error importing local settings file:\n"
        "\t%s\nDo you have a local_settings.py module?\n" % str(ex)
    )
