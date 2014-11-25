from django.conf.urls import patterns, include, url
from django.contrib import admin
from CSEducationTool.sodata.views import index, search_topics
from CSEducationTool import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'CSEducationTool.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'^$', index, name='index'),
    url(r'^search_topics', search_topics, name='search_topics'),

    #Heroku static files... why??
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),

)
