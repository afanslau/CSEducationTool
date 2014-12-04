from django.conf.urls import patterns, include, url
from django.contrib import admin
from sodata import views
from CSEducationTool import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'CSEducationTool.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'^topic', views.topic_request),
    url(r'^$', views.index, name='index'),
    url(r'^search_topics', views.search_topics, name='search_topics'),
    url(r'^createTopic', views.create_topic_form),
    url(r'^save_topic_edits', views.save_topic_edits),

    #Heroku static files... why??
    #http://stackoverflow.com/questions/21141315/django-static-files-on-heroku
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),

)
