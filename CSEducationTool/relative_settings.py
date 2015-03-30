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
            'filename': os.path.join(BASE_DIR,'logs','knowd_system.log'),
            'formatter': 'verbose'
        },
        'user-activity': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR,'logs','knowd_user_activity.log'),
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