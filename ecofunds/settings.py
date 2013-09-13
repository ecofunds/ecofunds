# coding: utf-8
import os
from sys import argv

from decouple import Config
from dj_database_url import parse as db_url
from unipath import Path

gettext = lambda s: s

PROJECT_ROOT = Path(__file__).parent

config = Config(PROJECT_ROOT.child('settings.ini'))

DEBUG = config('DEBUG', default=False, cast=bool)
TEMPLATE_DEBUG = DEBUG

GOOGLE_KEY = config('GOOGLE_KEY')
#GEOS_LIBRARY_PATH = 'C:/OSGeo4W/lib/geos_c_i.lib'

ADMINS = (
    ('Administrator', 'administrator@ecofunds.org'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': config('DATABASE_URL', cast=db_url)
}

if len(argv) > 1 and argv[1] == "test":
    DATABASES = { ########## IN-MEMORY TEST DATABASE
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
            "USER": "",
            "PASSWORD": "",
            "HOST": "",
            "PORT": "",
        },
    }

# Email Configuration

VALIDATE_EMAIL_URL = "localhost:8000/user/validate/"  # FIXME: ?
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Sao_Paulo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-US'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

MEDIA_ROOT = PROJECT_ROOT.child('media')
MEDIA_URL = '/media/'

STATIC_ROOT = PROJECT_ROOT.child('static')
STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    PROJECT_ROOT.child('assets'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = config('SECRET_KEY')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.filesystem.Loader',
    #'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'sekizai.context_processors.sekizai',
    'cms.context_processors.media',
    'ecofunds.context_processors.user',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    #'cms.middleware.media.PlaceholderMediaMiddleware',
)

ROOT_URLCONF = 'ecofunds.urls'

TEMPLATE_DIRS = (
    PROJECT_ROOT.child('templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'suit',
    'django.contrib.admin',
    #'south',
    'cms',
    'cms.plugins.picture',
    'cms.plugins.text',
    'cms.plugins.link',
    'cms.plugins.file',
    #'cmsplugin_news',
    'mptt',
    'menus',
    'appmedia',
    'sekizai',
    'tinymce',
    'babel',
    'xlwt',
    #'endless_pagination',
    'ecofunds.core',
    'ecofunds.user',
    'ecofunds.maps',
    'ecofunds.project',
    'ecofunds.organization',
    'ecofunds.investment',
    'ecofunds.crud',
    'ecofunds.geonames',
)

CMS_MEDIA_ROOT = STATIC_ROOT.child('cms')
CMS_MEDIA_URL = '/static/cms'

CMS_TEMPLATES = (
    ('home-template.html', gettext('Home Template')),
    ('main-template.html', gettext('Main Template')),
    ('institutional-template.html', gettext('Institutional Template')),
    ('default-template.html', gettext('Default Template')),
    ('form-template.html', gettext('Form Template'))
)


#AUTHENTICATION_BACKENDS = (
#    'ecofunds.auth_backends.CustomUserModelBackend',
#)
AUTH_PROFILE_MODULE = 'user.UserProfile'
#CUSTOM_USER_MODEL = 'ecofunds.user.models.CustomUser'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'sqlhandler': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'sql'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'sql': {
            '()': 'ecofunds.sqlformatter.SqlFormatter',
            'format': '%(levelname)s %(message)s',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['sqlhandler'],
            'level': 'DEBUG',
        },
        'maps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

AJAX_LOOKUP_CHANNELS = {
    'organization': ('ecofunds.lookups', 'OrganizationLookUp'),
    'location': ('ecofunds.lookups', 'LocationLookUp'),
    'activity': ('ecofunds.lookups', 'ActivityLookUp'),
    'userprofile': ('ecofunds.lookups', 'UserProfileLookUp'),
    'project': ('ecofunds.lookups', 'ProjectLookUp'),
    'country': ('ecofunds.lookups', 'CountryLookUp'),
    'investment': ('ecofunds.lookups', 'InvestmentLookUp'),
}

AJAX_SELECT_BOOTSTRAP = False
AJAX_SELECT_INLINES = 'inline'

CACHE = {
    'default': {
        'BACKEND': 'django.core.cache.backend.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 3000
    }
}
