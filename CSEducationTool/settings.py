''' COMMON SETTINGS '''
import os

#CUSTOM SETTINGS
BING_API_BASE = "https://api.datamarket.azure.com/Bing/"
BING_USERNAME = 'afanslau@gmail.com'
BING_PASSWORD = 'aPA1Hr8rGzCUyPMCEpxFOFWfpHLL0RvisEFc1Q+mJsE'


# relative_settings default values
BASE_DIR = os.path.dirname(__file__)
BASE_URL = '/'

CSRF_COOKIE_SECURE = False

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

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True





