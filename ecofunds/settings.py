import os
gettext = lambda s: s

import matplotlib
matplotlib.use('Agg')

from unipath import Path

PROJECT_PATH = Path(__file__).parent

GOOGLE_KEY = 'AIzaSyAZpfiGAvTO1zpd-eWWZcbkHm40BrFp0tI'
#GEOS_LIBRARY_PATH = 'C:/OSGeo4W/lib/geos_c_i.lib'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Administrator', 'administrator@ecofunds.org'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'ecofunds',                   # Or path to database file if using sqlite3.
        'USER': 'root',                   # Not used with sqlite3.
        'PASSWORD': '',               # Not used with sqlite3.
        'HOST': '',                # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                           # Set to empty string for default. Not used with sqlite3.
    }
}

# Email Configuration

VALIDATE_EMAIL_URL = "localhost:8000/user/validate/"
EMAIL_HOST = ""
EMAIL_PORT = 587
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = True

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pt-br'

LANGUAGES = [
    ('pt-br', 'Brazilian Portuguese'),
    ('en', 'English'),
    ('es', 'Espanol')
]

LANGUAGES_DATEFORMAT = {
    'pt-br':'dd/mm/yy',
    'en':'mm/dd/yy',
    'es':'dd/mm/yy',
}

LANGUAGES_NUMBERFORMAT = {
    'pt-br':'decimal',
    'en':'decimal-us',
    'es':'decimal',
}

DEFAULT_LANGUAGE = 0
SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

MEDIA_ROOT = PROJECT_PATH.child('static').child('media')
MEDIA_URL = '/static/media/'

STATIC_ROOT = PROJECT_PATH.child('assets')
STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/static/admin/'

GEOIP_DATABASE = PROJECT_PATH.child('geoip').child('GeoLiteCity.dat')

# Additional locations of static files
STATICFILES_DIRS = (
    PROJECT_PATH.parent.child('static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
# FIXME: remove before stage deploy
SECRET_KEY = '^28avlv8e$sky_08pu926q^+b5&4&5&+ob7ma%v(tn$bg#=&k4'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
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
    #'cms.middleware.multilingual.MultilingualURLMiddleware',
    'ecofunds.middleware.multilingual.CustomMultilingualURLMiddleware',
    'ecofunds.middleware.forcedresponse.ForceResponseMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    #'cms.middleware.media.PlaceholderMediaMiddleware',
)

ROOT_URLCONF = 'ecofunds.urls'

TEMPLATE_DIRS = (
    PROJECT_PATH.child('templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'cms',
    'cms.plugins.picture',
    'cms.plugins.text',
    'cms.plugins.link',
    'cms.plugins.file',
    #'cmsplugin_news',
    'mptt',
    'menus',
    'south',
    'appmedia',
    'sekizai',
    'pygeoip',
    'tinymce',
    'babel',
    'xlwt',
    'ajax_select',
    'rosetta',
    #'endless_pagination',
    'ecofunds',
    'ecofunds.user',
    'ecofunds.maps',
    'ecofunds.opportunity',
    'ecofunds.project',
    'ecofunds.organization',
    'ecofunds.investment',
)

CMS_MEDIA_ROOT = PROJECT_PATH.child('static').child('cms')
CMS_MEDIA_URL= '/static/cms'

CMS_TEMPLATES = (
    ('home-template.html', gettext('Home Template')),
    ('main-template.html', gettext('Main Template')),
    ('institutional-template.html', gettext('Institutional Template')),
    ('default-template.html', gettext('Default Template')),
    ('form-template.html', gettext('Form Template'))
)

CMS_LANGUAGE_CONF = {
    'pt-br':['en'],
    'en':['pt-br'],
    'es':['en'],
}

CMS_LANGUAGES = (
    ('pt-br', gettext('Brazilian Portuguese')),
    ('en', gettext('English')),
    ('es', gettext('Espanol')),
)
CMS_SITE_LANGUAGES = {
    1:['pt-br','en', 'es'],
}
CMS_FRONTEND_LANGUAGES = ('pt-br', 'en', 'es')

CMS_APPLICATIONS_URLS = (
    #('cmsplugin_news.urls', 'News'),
    ('ecofunds.opportunity.urls', 'Funding Oportunity'),
)
CMS_NAVIGATION_EXTENDERS = (
    #('cmsplugin_news.navigation.get_nodes','News navigation'),
    ('ecofunds.opportunity.navigation.get_nodes','Funding Oportunity Navigation'),
)

URLS_WITHOUT_LANGUAGE_REDIRECT = [
    'css',
    'js',
]

#CONFIGURACOES ROSETTA
ROSETTA_MESSAGES_PER_PAGE = 50
ROSETTA_ENABLE_TRANSLATION_SUGGESTIONS = True
ROSETTA_WSGI_AUTO_RELOAD = True


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
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
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

AJAX_LOOKUP_CHANNELS = {
    'organization':('ecofunds.lookups','OrganizationLookUp'),
    'location':('ecofunds.lookups','LocationLookUp'),
    'activity':('ecofunds.lookups','ActivityLookUp'),
    'userprofile':('ecofunds.lookups','UserProfileLookUp'),
    'project':('ecofunds.lookups','ProjectLookUp'),
    'country':('ecofunds.lookups','CountryLookUp'),
    'investment':('ecofunds.lookups','InvestmentLookUp'),
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
