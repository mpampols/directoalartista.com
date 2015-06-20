# Django project environment-specific settings

from directoalartista.settings.base import *

DEBUG = TEMPLATE_DEBUG = False
ALLOWED_HOSTS = [".directoalartista.com"]

BASE_URL = "https://www.directoalartista.com"

SITE_ID = 1

DEFAULT_FROM_EMAIL = 'info@directoalartista.com'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'directoalartista.wsgi-prod.application'

TIME_ZONE = 'Europe/Madrid'

INTERNAL_IPS = ('127.0.0.1', )

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211'
    }
}

CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Paypal real
PAYPAL_RECEIVER_EMAIL = ""
PAYPAL_IDENTITY_TOKEN = ""
PAYPAL_NOTIFY_URL = ""
PAYPAL_RETURN_URL = ""
PAYPAL_CANCEL_RETURN = ""
PAYPAL_API_USERNAME = ""
PAYPAL_API_PASSWORD = ""
PAYPAL_API_SIGNATURE = ""
PAYPAL_API_URL = 'https://api-3t.paypal.com/nvp'
PAYPAL_URL = 'https://www.paypal.com/cgi-bin/webscr'

# Overwrite default ROOT_URLCONF to include static file serving by Django.
# In production, this should be handled separately by your webserver or CDN.
# ROOT_URLCONF = 'directoalartista.urls.dev'
ROOT_URLCONF = 'directoalartista.urls'
