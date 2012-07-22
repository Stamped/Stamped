# Django settings for www project.

import Globals
import utils, os, libs.ec2_utils

IS_PROD         = libs.ec2_utils.is_prod_stack()
DEBUG           = (not IS_PROD)
STAMPED_DEBUG   = (not utils.is_ec2())
TEMPLATE_DEBUG  = DEBUG
PROJ_ROOT       = os.path.abspath(os.path.dirname(__file__))

STAMPED_ASSET_VERSION       = utils.shell("cd %s && make version" % PROJ_ROOT)[0]
STAMPED_DOWNLOAD_APP_LINK   = "http://itunes.apple.com/us/app/stamped/id467924760?mt=8&uo=4"

utils.log("Django DEBUG=%s ROOT=%s VERSION=%s" % (DEBUG, PROJ_ROOT, STAMPED_ASSET_VERSION))

ADMINS = (
    ('Travis', 'travis@stamped.com'), 
)

MANAGERS  = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

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
# Example: "/home/media/media.lawrence.com/media/"
#MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
#MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/assets/'

# utilize static.stamped.com CDN gateway on ec2; otherwise, fallback to using 
# less efficient but more accessible / productive local assets for development.
if IS_PROD:
    SITE_ROOT   = "http://static.stamped.com"
else:
    SITE_ROOT   = PROJ_ROOT

if STAMPED_DEBUG:
    STAMPED_STATIC_URL  = STATIC_URL
else:
    STAMPED_STATIC_URL  = "%s%sgenerated/" % ("http://static.stamped.com", STATIC_URL)

STATIC_DOC_ROOT = SITE_ROOT

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(STATIC_DOC_ROOT, 'assets'), 
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'aw$jm6l=^ut&u=2n@7!!#&ds^1s!dqrywkvw2x&x_@g^rhsivh'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware', 
)

ROOT_URLCONF = 'web2.urls'

STAMPED_TEMPLATE_DIR  = os.path.join(PROJ_ROOT, "html")
STAMPED_TEMPLATE_DIR2 = os.path.join(PROJ_ROOT, "templates")
STAMPED_TEMPLATE_FILE = os.path.join(STAMPED_TEMPLATE_DIR2, "templates.generated.html")

STAMPED_PROFILE_TEMPLATE_FILE = os.path.join(STAMPED_TEMPLATE_DIR2, "profile.generated.html")
STAMPED_MAP_TEMPLATE_FILE     = os.path.join(STAMPED_TEMPLATE_DIR2, "map.generated.html")

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    STAMPED_TEMPLATE_DIR, 
)

# A tuple of strings representing allowed prefixes for the {% ssi %} template 
# tag. This is a security measure, so that template authors can't access files 
# that they shouldn't be accessing.
# 
# For example, if ALLOWED_INCLUDE_ROOTS is ('/home/html', '/var/www'), then 
# {% ssi /home/html/foo.txt %} would work, but {% ssi /etc/passwd %} wouldn't.
ALLOWED_INCLUDE_ROOTS = (
    STAMPED_TEMPLATE_DIR, 
    STAMPED_TEMPLATE_DIR2, 
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core', 
)

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

