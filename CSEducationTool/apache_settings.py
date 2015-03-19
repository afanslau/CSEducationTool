"""
Django settings for CSEducationTool project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from CSEducationTool.global_settings import *

DB_NAME = "myproj_db" # "smallsodata"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": DB_NAME,
        "USER": "myproj_user",
        "PASSWORD": "123",
        "HOST": "localhost",
        "PORT": "",
    }
}

DEBUG = False
ALLOWED_HOSTS = ['.cs.drew.lan', '.cs.drew.edu']

# Override default relative paths
BASE_DIR = os.path.dirname(__file__)
BASE_URL = '/knowd/'

# Find the right way to do this without copying and pasting
# from relative_settings import *
# BASE_URL not defined

# Javascript Reverse URL Lookup
JS_REVERSE_SCRIPT_PREFIX = BASE_URL

LOGIN_REDIRECT_URL = BASE_URL



STATIC_ROOT = 'staticfiles'
STATIC_URL = os.path.join(BASE_URL, 'static/')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static/'),
)

#Don't actually need this, since the django.template.loaders.app_directories.Loader looks for the templates directory under each running app.
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'sodata/templates/'),
    os.path.join(BASE_DIR, 'templates/'),
)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'django-core': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'apache','logs','knowd_system.log'),
            'formatter': 'verbose'
        },
        'user-activity': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR,'apache','logs','knowd_user_activity.log'),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers':['django-core'],
            'propagate': True,
            'level':'DEBUG',
        },
        'sodata': {
            'handlers': ['user-activity'],
            'level': 'DEBUG',
        },
    }
}






# DATABASES['default'] =  dj_database_url.config()


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

# LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'

# USE_I18N = True

# USE_L10N = True

# USE_TZ = True


# # Static files (CSS, JavaScript, Images)
# # https://docs.djangoproject.com/en/1.7/howto/static-files/

# STATIC_ROOT = 'staticfiles'


# # STATICFILES_DIRS = (
# #     os.path.join(BASE_DIR, 'sodata/static/'),
# # )

# #Don't actually need this, since the django.template.loaders.app_directories.Loader looks for the templates directory under each running app.
# TEMPLATE_DIRS = (
#     os.path.join(BASE_DIR, 'sodata/templates/'),
# )
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
