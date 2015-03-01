import os, sys
#sys.path.append('/var/www/django')
#sys.path.append('/var/www/django/CSEducationTool')
os.environ['DJANGO_SETTINGS_MODULE'] = 'CSEducationTool.apache_settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

#import django.core.handlers.wsgi
#application = django.core.handlers.wsgi.WSGIHandler()
