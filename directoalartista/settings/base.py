# Django settings for directoalartista project.

# Common settings and globals.

import os
import sys
import directoalartista as project_module

PROJECT_ROOT = os.path.dirname(os.path.realpath(project_module.__file__))

BASE_URL = "https://www.directoalartista.com"

ADMINS = (
    ('Directo al Artista', 'admin@directoalartista.com'),
)

MANAGERS = ADMINS

SITE_ID = 1

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Madrid'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es'

DEFAULT_CHARSET = 'utf-8'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, 'assets'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# List of callables variables in contextprocessors
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',

    # Required by allauth template tags
    'django.core.context_processors.request',

    # allauth specific context processors
    'allauth.account.context_processors.account',
    'allauth.socialaccount.context_processors.socialaccount',

    'django.contrib.messages.context_processors.messages',
    'directoalartista.apps.transaction.context_processors.paypal_variables',
)

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'directoalartista.apps.utilities.middleware.XUACompatibleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'pipeline.middleware.MinifyHTMLMiddleware',
)

ROOT_URLCONF = 'directoalartista.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # django-allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # django-allauth providers
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.openid',
    'allauth.socialaccount.providers.soundcloud',
    'allauth.socialaccount.providers.tumblr',
    'allauth.socialaccount.providers.twitter',
    'allauth.socialaccount.providers.vimeo',

    # directoalartista apps
    'directoalartista.apps.contact',
    'directoalartista.apps.myaccount',
    'directoalartista.apps.genericuser',
    'directoalartista.apps.plancontrol',
    'directoalartista.apps.artistprofile',
    'directoalartista.apps.transaction',
    'directoalartista.apps.invoicing',

    # paypal
    'paypal.standard.pdt',
    'paypal.standard.ipn',

    'localflavor',
    'premailer',
    'djmoney',
    'categories',
    'categories.editor',
    'django.contrib.sitemaps',
    'django.contrib.flatpages',
    'django.contrib.humanize',
    'pipeline'
)

AUTH_PROFILE_MODULE = "genericuser.GenericUser"

# Upgrade to 1.7.1
AUTH_USER_MODEL = 'genericuser.GenericUser'

# Django-allauth
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'email'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_SIGNUP_FORM_CLASS = 'directoalartista.apps.genericuser.forms.GenericUserCustomRegistrationFormArtist'

# Params for file upload
FILE_UPLOAD_MAX_MEMORY_SIZE = 44040192

# Params for django-registration
#ACCOUNT_ACTIVATION_DAYS = 2
#REGISTRATION_OPEN = True

# Mailchimp
MAILCHIMP_LIST_ID = ''
MAILCHIMP_API = ''

# Email configuration
DEFAULT_FROM_EMAIL = 'Directo al Artista <noreply@directoalartista.com>'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = ''
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = 'DAA ERROR: '

# Emails admins
MAIL_ADMIN_WEB = 'admin@directoalartista.com'
MAIL_ADMIN_INVOICE = 'info@directoalartista.com'
MAIL_INFO = 'info@directoalartista.com'
MAIL_NOREPLY = 'noreply@directoalartista.com'

# Transaction and invoicing parameters
INVOICE_LOGO = os.path.join(PROJECT_ROOT, 'assets/img/invoice_logo.png')
DATE_FORMAT = "%d-%m-%Y"
VAT_SPAIN = 0.21
CONTACT_PRICE = 9.99
SUBSCRIPTION_FREE = 0
SUBSCRIPTION_STARTER = 4.99
SUBSCRIPTION_UNLIMITED = 24.99

USER_LIMITS = {
    "artistprofile_max_secondarycategories_4": 0,
    "artistprofile_max_secondarycategories_3": 1,
    "artistprofile_max_secondarycategories_2": 5,
    "artistprofile_max_secondarycategories_1": 5,
    "artistprofile_max_eventtypes_4": 2,
    "artistprofile_max_eventtypes_3": 6,
    "artistprofile_max_eventtypes_2": 6,
    "artistprofile_max_eventtypes_1": 6,
    "artistprofile_max_provinces_4": 2,
    "artistprofile_max_provinces_3": 4,
    "artistprofile_max_provinces_2": 99,
    "artistprofile_max_provinces_1": 99,
    "artistprofile_max_pictures_4": 1,
    "artistprofile_max_pictures_3": 7,
    "artistprofile_max_pictures_2": 7,
    "artistprofile_max_pictures_1": 7,
    "artistprofile_max_videos_4": 1,
    "artistprofile_max_videos_3": 7,
    "artistprofile_max_videos_2": 7,
    "artistprofile_max_videos_1": 7
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

from django.core.exceptions import SuspiciousOperation

def skip_suspicious_operations(record):
    if record.exc_info:
        exc_value = record.exc_info[1]
        if isinstance(exc_value, SuspiciousOperation):
            return False
    return True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        # Skip suspicious operations
        'skip_suspicious_operations': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_suspicious_operations,
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false', 'skip_suspicious_operations'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Set the session engine
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

# Pipeline storage for STATICFILES_STORAGE used by django-pipeline
STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

PIPELINE_CSS = {
    'bootstrap': {
        'source_filenames': (
            'css/bootstrap.css',
            'css/normalize.css',
        ),
        'output_filename': 'css/bootstrap.min.css',
    },
    'app': {
        'source_filenames': (
            'css/main.css',
        ),
        'output_filename': 'css/app.min.css',
    },
    '3rdparty': {
        'source_filenames': (
            'css/jquery.cookiebar.css',
            'css/colorbox.css',
        ),
        'output_filename': 'css/3rdparty.min.css',
    },
    'print': {
        'source_filenames': (
            'css/print.css',
        ),
        'output_filename': 'css/print.min.css',
        'extra_context': {
            'media': 'print',
        },
    },
}

PIPELINE_JS = {
    'vendor': {
        'source_filenames': (
          'js/vendor/bootstrap.js',
          'js/vendor/jquery.colorbox.js',
          'js/vendor/jquery.cookiebar.js',
          'js/vendor/jquery.form.js',
        ),
        'output_filename': 'js/vendor.js',
    },
    'app': {
        'source_filenames': (
          'js/main.js',
        ),
        'output_filename': 'js/app.js',
    }
}

# Changes needed to use https only
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Fix for 1_6.Woo1 warning on manage check (Django 1.6 new test runners)
TEST_RUNNER = 'django.test.runner.DiscoverRunner'