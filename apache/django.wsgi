import os, sys
#sys.path.append('/var/www/django')
#sys.path.append('/var/www/django/CSEducationTool')
os.environ['DJANGO_SETTINGS_MODULE'] = 'CSEducationTool.apache_settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
	sys.path.append(path)

#import django.core.handlers.wsgi
#application = django.core.handlers.wsgi.WSGIHandler()
