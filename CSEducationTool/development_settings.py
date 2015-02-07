"""
Django settings for CSEducationTool project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from settings import *


# BASE_DIR = os.path.dirname(__file__)



# DB_NAME = "topicdb" # "smallsodata"

# # Quick-start development settings - unsuitable for production
# # See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# # SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'xhpdufz^9&6d7f1aek_hgrsozb!c(p4m7&7xz0!_3vm5utx%&q'

# # SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True

# TEMPLATE_DEBUG = True

# ALLOWED_HOSTS = []


# # Application definition

# INSTALLED_APPS = (
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     'sodata'
# )

# MIDDLEWARE_CLASSES = (
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# )

# ROOT_URLCONF = 'CSEducationTool.urls'

# WSGI_APPLICATION = 'CSEducationTool.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": DB_NAME,
        "USER": "afanslau",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": "",
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
# STATIC_URL = '/static/'

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