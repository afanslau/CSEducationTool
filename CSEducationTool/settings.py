"""
Django settings for CSEducationTool project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

#CUSTOM SETTINGS
BING_API_BASE = "https://api.datamarket.azure.com/Bing/"
BING_USERNAME = 'afanslau@gmail.com'
BING_PASSWORD = 'aPA1Hr8rGzCUyPMCEpxFOFWfpHLL0RvisEFc1Q+mJsE'


BASE_DIR = os.path.dirname(__file__)

CSRF_COOKIE_SECURE = False


DB_NAME = 'small_temp' # 'topicdb' #Using small_temp for testing the watson search   # Was 

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xhpdufz^9&6d7f1aek_hgrsozb!c(p4m7&7xz0!_3vm5utx%&q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_js_reverse',
    'watson',
    'sodata',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

APPEND_SLASH=True

ROOT_URLCONF = 'CSEducationTool.urls'

WSGI_APPLICATION = 'CSEducationTool.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql_psycopg2",
#         "NAME": DB_NAME,
#         "USER": "",
#         "PASSWORD": "",
#         "HOST": "localhost",
#         "PORT": "",
#     }
# }

# DATABASES['default'] =  dj_database_url.config()


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True



# Auth
LOGIN_REDIRECT_URL = '/'



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = 'staticfiles'
STATIC_URL = 'static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static/'),
)

#Don't actually need this, since the django.template.loaders.app_directories.Loader looks for the templates directory under each running app.
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'sodata/templates/'),
    os.path.join(BASE_DIR, 'templates/'),
)
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.





