# Django project environment-specific settings

from directoalartista.settings.base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']

BASE_URL = "http://www.directoalartista.dev:8888"

SITE_ID = 1

#TODO: replace localhost with the domain name of the site
DEFAULT_FROM_EMAIL = ''
SERVER_EMAIL = DEFAULT_FROM_EMAIL

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                       # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                       # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                       # Set to empty string for default.
    }
}

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'directoalartista.wsgi-dev.application'

TIME_ZONE = 'Europe/Madrid'

INTERNAL_IPS = ('127.0.0.1', )

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, 'assets'),
)

# Paypal Sandbox for test only
PAYPAL_RECEIVER_EMAIL = ""
PAYPAL_IDENTITY_TOKEN = ""
PAYPAL_NOTIFY_URL = ""
PAYPAL_RETURN_URL = ""
PAYPAL_CANCEL_RETURN = ""
PAYPAL_API_USERNAME = ""
PAYPAL_API_PASSWORD = ""
PAYPAL_API_SIGNATURE = ""
PAYPAL_API_URL = 'https://api-3t.sandbox.paypal.com/nvp'
PAYPAL_URL = 'https://www.sandbox.paypal.com/cgi-bin/webscr'

# Overwrite default ROOT_URLCONF to include static file serving by Django.
# In production, this should be handled separately by your webserver or CDN.
ROOT_URLCONF = 'directoalartista.urls.dev'

# Using dummy cache for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
   }
}

# Disable SSL on development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Enable logging on file
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}