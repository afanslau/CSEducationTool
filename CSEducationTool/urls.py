from django.conf.urls import patterns, include, url
from django.contrib import admin
from sodata import views
from CSEducationTool import settings

'''

api/{version}

Global parameters
format=xml,json

http://www.vinaysahni.com/best-practices-for-a-pragmatic-restful-api#restful

GET /resources ? q- get all resources
GET /resources/{id} - get a single resource

GET /resources/standard ? q - get the entire standard library
GET /resources/standard/{unique_title} - get a specific standard resource 

GET /resources/{id}/resourceList ? q - get all children for a resource
GET /resources/{id}/parentTopics ? q - get all parents for a resource

POST /resources/create ? title, text, url - create a new resource
POST /resources/{id}/fork ? title, text, url - create a new resource with a link to id

POST /relations/{parent_id}/create/{child_id} - link the parent to the child

DELETE /relations/{parent_id}/unlink/{child_id} - unlink the parent to the child
DELETE /relations/delete/{id} - delete the given relationship  
DELETE /resources/delete/{id} - delete the given resource

PUT 
/resources/{id}/update ? title, text, url

'''

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'CSEducationTool.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # Login Authentication
    url(r'^register$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout'),

    url(r'^fts$', views.fts),


    # USER INTERFACE
    url(r'^resources/create/(?P<parent_id>\d+)$', views.ui_create_resource, name='ui_create_resource_in_topic'), 
    url(r'^resources/create$', views.ui_create_resource, name='ui_create_resource_in_root'), 
    url(r'^resources/update/(?P<resource_id>\d+)$', views.ui_update_resource, name='ui_update_resource'), 
    url(r'^resources/(?P<resource_id>\d+)$', views.ui_get_resource, name='ui_get_resource'),
    # Note:  $ matches the end of a string. Don't use here to allow for optional end / . This should probably be used everywhere??
    url(r'^resources/search', views.ui_search_resources, name='ui_search_resources'),
    url(r'^resources', views.ui_get_resource, name='ui_get_root_resource'),





    # '''  REST  API  - NOT FULLY TESTED'''


    # '''  Creates a stand-alone resource 
    # POST /resources/create ? title, text, url - create a new resource '''
    url(r'^api/resources/create$', views.api_create_resource, name='create_resource'), 

    # '''  Create a resource under the given topic 
    # POST /resources/{id}/create ? title, text, url - create a new resource in the given topic '''
    url(r'^api/resources/create/(?P<resource_id>\d+)$', views.api_create_resource, name='create_resource_in_topic'), 

    # '''  Update a given resource
    # POST /resources/{id}/update ? title, text, url - set data for the given resource '''
    url(r'^api/resources/update/(?P<resource_id>\d+)$', views.api_update_resource, name='api_update_resource'), 
    
    # '''  Update a given resource
    # POST /resources/{id}/update ? title, text, url - set data for the given resource '''
    url(r'^api/resources/upvote/(?P<resource_id>\d+)$', views.api_rate_resource, name='api_rate_resource', kwargs={'rating':1}),

    # '''  Update a given resource
    # POST /resources/{id}/update ? title, text, url - set data for the given resource '''
    url(r'^api/resources/downvote/(?P<resource_id>\d+)$', views.api_rate_resource, name='api_rate_resource', kwargs={'rating':-1}),     

    # ''' Get the resource by its id 
    # GET /resources/{id} - get a single resource '''
    url(r'^api/resources/(?P<resource_id>\d+)$', views.api_get_resource, name='get_resource'),
    
    # ''' Deletes a resource by passing the resource id 
    # HTTP DELETE /resources/delete/{id} - delete the given resource '''
    url(r'^api/resources/delete/(?P<resource_id>\d+)$', views.api_delete_resource, name='delete_resource'), 

    # ''' Get all resources matching the specified query
    # GET /resources ? q- get all resources '''
    url(r'^api/resources', views.api_search_resources, name='search_resources'),

    # '''  Create a relation 
    # POST /relations/{parent_id}/create/{child_id} - link the parent to the child '''
    url(r'^api/relations/(?P<parent_id>\d+)/create/(?P<child_id>\d+)$', views.api_create_relation, name='create_relation'), 

    # '''  Delete a relation by passing its connecting resources 
    # HTTP DELETE /relations/{parent_id}/delete/{child_id} - unlink the parent to the child '''
    url(r'^api/relations/(?P<parent_id>\d+)/delete/(?P<child_id>\d+)$', views.api_delete_relation_by_resources, name='delete_relation_by_resource'), 
    
    # ''' Deletes a relation by passing the relation id 
    # HTTP DELETE /relations/delete/{id} - delete the given relationship '''
    url(r'^api/relations/delete/(?P<relation_id>\d+)$', views.api_delete_relation_by_id, name='delete_relation_by_id'), 







    url(r'^admin/', include(admin.site.urls), name='admin'),
    # url(r'^topic', views.topic_request),
    url(r'^$', views.ui_get_resource, name='index'),
    # url(r'^search_topics', views.search_topics, name='search_topics'),
    # url(r'^createTopic', views.create_topic_form),
    # url(r'^save_topic_edits', views.save_topic_edits),
    # url(r'^resources/save', views.save_resource),
    

    #Heroku static files... why??
    # Cite: http://stackoverflow.com/questions/21141315/django-static-files-on-heroku
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    # End Cite
)
