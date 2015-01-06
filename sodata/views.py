from django.shortcuts import render, render_to_response
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth import authenticate, login

from sodata.models import TopicRelations, Resources
from sodata.searchHelper import get_query
from sodata.forms import ResourceForm, SignupForm, LoginForm

import watson


import json, re 
import Bing
from bs4 import BeautifulSoup as Soup

'''
select min(id), max(id) from sodata_resources;
 min  | max  
------+------
 1719 | 1877

'''


ui_topic_base_url = 'resources/%d'

''' Render and return the topic template page '''
def ui_get_resource(request, resource_id=None):

    if resource_id is None:
        #Return top level topics

        # Parent is fake, just for display purposes. This probably has to change
        parent = Resources(title='This is the home page',text='This is a website where you can explore computer science topics. You can store good resources you find, and share them with others.')
        topics = Resources.objects.filter(parent_resources=None)
        topics = sorted(topics, key=lambda t: t.updated_at, reverse=True)
        external_search_results = None

    else:
        #Return one specific topic
        resource_id = int(resource_id)
        try:
            parent = Resources.objects.get(id=resource_id)
            topics = parent.get_child_resources()


            external_search_results = get_external_search(topic=parent)

            #Sort by updated_at
            if topics is not None:
                topics = sorted(topics, key=lambda t: t.updated_at, reverse=True)
            print('request - Render template with resource_id: %d  %s' % (parent.id, parent.title))
        except ObjectDoesNotExist:
            print('request - Render template with resource_id: %d  NOT FOUND' % resource_id)
            raise Http404






    data = {'resource':parent, 'resource_list':topics, 'external_search_results':external_search_results, 'user':request.user}
    return render_to_response('sodata/newtopic.html', data) #same-as  render(request, 'sodata/index.html', data)




def ui_edit_resource(request):
    if request.method=="POST":
        form = ResourceForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            new_resource = form.save(commit=False)

            if parent_id is None:
                new_resource.save()
                print('request - CREATE resource with data %s' % cd)
            else:
                try:
                    parent_id = int(parent_id)
                    parent = Resources.objects.get(id=parent_id)
                    new_resource.save()     
                    TopicRelations.objects.create(from_resource=parent, to_resource=new_resource)
                    print('request - CREATE resource under %s with data %s' % (parent.title, new_resource.to_dict()))
                except ObjectDoesNotExist:
                    print('request - CREATE resource under %d  NOT FOUND' % parent_id)
                    raise Http404



    else:
        form = ResourceForm()

    return render(request, 'resource_form.html', {'form': form})


''' GET /resources/{id} - get a single resource '''
def api_get_resource(request, resource_id):
    resource_id = int(resource_id)
    try:
        resource = Resources.objects.get(id=resource_id)
    except ObjectDoesNotExist:
        raise Http404

    print('request - GET resource id:%d  %s' % (resource_id, resource.title))
    return json_response(resource)


def ui_search_resources(request):
    ''' Basic keyword search attempt '''
    query_string = ''
    found_entries = None

    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        entry_query = get_query(query_string, ['title', 'text'])        
        found_entries = Resources.objects.filter(entry_query).order_by('-rating')
    else: found_entries = Resources.objects.all()

    if ('seed' in request.GET):
        val = request.GET['seed'].strip()
        if val=="True" or val=="1":
            seed = True
        elif val=="False" or val=="0":
            seed = False
        else: 
            return HttpResponseBadRequest
        found_entries = found_entries.filter(pre_seeded=seed)
    # Fake a resource for easy diplay
    parent = Resources(title="Search Results", text=query_string)
    return render_to_response('sodata/topic.html', { 'topic': parent, 'resource_list': found_entries })


def api_search_resources(request):
    q = request.GET.get('q')
    print ('request - search resources for q= %s' % q)
    return HttpResponse('Not Implemented')



''' POST /resources/{id}/create - create a resource in the given topic '''
''' POST /resources/create - create a stand-alone resource '''
def api_create_resource(request, parent_id=None):
    new_resource = create_resource(request, parent_id)
    return json_response(new_resource)

def ui_create_resource(request, parent_id=None):
    new_resource = create_resource(request, parent_id)
    data = {'resource':new_resource}
    return render_to_response('sodata/list_item.html', data)

def create_resource(request, parent_id=None):

    # parsed_urls = []
    # if request.POST.get('text') is not None and request.POST.get('url') is None:
    #   parsed_urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', request.POST.get('text'))
    #   print(parsed_urls)

    # if len(parsed_urls)>0 and (new_url is None or new_url == ''):
    #   new_url = parsed_urls[0]

    
    new_resource = Resources(title=request.POST.get('title'), text=request.POST.get('text'), url=request.POST.get('url'))

    if parent_id is None:
        new_resource.save()
        print('request - CREATE resource with data %s' % request.POST)
    else:
        try:
            parent_id = int(parent_id)
            parent = Resources.objects.get(id=parent_id)
            new_resource.save()     
            TopicRelations.objects.create(from_resource=parent, to_resource=new_resource)
            print('request - CREATE resource under %s with data %s' % (parent.title, new_resource.to_dict()))
        except ObjectDoesNotExist:
            print('request - CREATE resource under %d  NOT FOUND' % parent_id)
            raise Http404

    return new_resource


def api_update_resource(request, resource_id=None):
    if resource_id is None: raise Http404
    updated_resource = update_resource(request, resource_id)
    return json_response(updated_resource)

def ui_update_resource(request, resource_id=None):
    if resource_id is None: raise Http404
    updated_resource = update_resource(request, resource_id)
    data = {'resource':updated_resource}
    return render_to_response('sodata/resource_content.html', data)

def update_resource(request, resource_id=None):
    print('request - UPDATE resource with data %s' % request.POST)
    
    # Get the resource
    try:
        resource = Resources.objects.get(id=resource_id)
    except ObjectDoesNotExist:
        raise Http404







    # Update the content
    should_save = False
    new_title = request.POST.get('title')
    if new_title is not None:
        resource.title = new_title if new_title != '' else None
        should_save = True

    new_text = request.POST.get('text')

    parsed_urls = []
    if request.POST.get('text') is not None and request.POST.get('url') is None:
        parsed_urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', request.POST.get('text'))
        print(parsed_urls)
    if new_text is not None:
        resource.text = new_text if new_text != '' else None
        should_save = True



    new_url = request.POST.get('url')
    if len(parsed_urls)>0 and (new_url is None or new_url == ''):
        new_url = parsed_urls[0]

    # new_url = request.POST.get('url')
    if new_url is not None:
        resource.url = new_url if new_url != '' else None
        should_save = True

    if should_save: resource.save()
    return resource


def api_rate_resource(request, resource_id=None, rating=0):
    return json_response(rate_resource(resource_id=resource_id, rating=rating))
    
def rate_resource(resource_id=None, rating=0):
    try: 
        resource = Resources.objects.get(id=resource_id)
    except ObjectDoesNotExist:
        raise Http404

    resource.rating += rating
    resource.save()
    return resource



def api_delete_resource(request, resource_id=None):
    if resource_id is None: return HttpResponse()
    resource_id = int(resource_id)
    print('request - Delete %d' % resource_id)
    try:
        to_delete = Resources.objects.get(id=resource_id)
    except ObjectDoesNotExist:
        print('request - DELETE resource %d  NOT FOUND' % resource_id)
        raise Http404
    print('request - DELETE resource %d  %s' % (resource_id, to_delete.title))
    to_delete.delete()
    return json_response(to_delete)



''' POST /relations/{parent_id}/create/{child_id} - link the parent to the child '''
def api_create_relation(request, parent_id, child_id):
    parent_id, child_id = int(parent_id), int(child_id)
    try:
        relation = create_relation(parent_id, child_id)
    except ObjectDoesNotExist:
        print('request - CREATE relation from %d to %d  NOT FOUND' % (parent_id, child_id))
        raise Http404
    print('request - CREATE relation from %d %s to %d %s ' % (relation.from_resource.id, relation.from_resource.title, relation.to_resource.id, relation.to_resource.title))
    return HttpResponse(json.dumps(relation.to_dict()))

def create_relation(parent_id, child_id):
    parent = Resources.objects.get(id=parent_id)
    child = Resources.objects.get(id=child_id)
    relation = TopicRelations(from_resource=parent, to_resource=child)
    relation.save()
    print('request - Create relation from %s to %s' % (parent.title, child.title))
    return relation 
def api_delete_relation_by_id(request, relation_id):
    relation_id = int(relation_id)
    try:
        to_delete = TopicRelations.objects.get(id=relation_id)
    except ObjectDoesNotExist:
        print('request - DELETE relation_id: %d NOT FOUND' % relation_id)
        raise Http404
    print('request - DELETE relation from %s to %s' % (to_delete.from_resource.title, to_delete.to_resource.title))
    to_delete.delete()
    return json_response(to_delete)

def api_delete_relation_by_resources(request, parent_id, child_id):
    parent_id, child_id = int(parent_id), int(child_id)
    try:
        to_delete = TopicRelations.objects.get(from_resource=parent_id, to_resource=child_id)
    except ObjectDoesNotExist:
        print('request - DELETE relation from %d to %d NOT FOUND' % (parent_id, child_id))
        raise Http404
    print('request - DELETE relation from %s to %s' % (to_delete.from_resource.title, to_delete.to_resource.title))
    to_delete.delete()
    return json_response(to_delete)





''' Helper function - render a json response for a given resource '''
def json_response(resource):
    if resource is None: raise Http404
    try: # make a list of json serializable dictionaries 
        out = [r.to_dict() for r in resource]
    except TypeError: #resource is one resource.. Not iterable
        out = resource.to_dict()
    return HttpResponse(json.dumps(out))









# Concatenates a list of search terms
# Returns a list of resources to display
def get_external_search(topic=None, related_topics=None):
    # First check the cache
    external_cached = topic.get_child_resources(human_created=False)
    if external_cached is not None:
        return external_cached

    # If nothing exists, or it is stale by t seconds/../days
    # First create search query using topic
    if topic is None: return []
    if related_topics is None: 
        related = []
    else:
        related = related_topics
    search_terms = [topic.title]
    query_term = ' '.join(search_terms)

    # Then execute the query
    soup = Soup(Bing.perform_query(query_term))
    search_results = [e.find('content') for e in soup.find_all('entry')]

    # Cache the results
    resources = []
    for r in search_results:
        title = r.find('d:title').text 
        text=r.find('d:description').text
        url=r.find('d:url').text
        display_url = r.find('d:displayurl').text
        bing_id = r.find('d:id').text
        resource, created = Resources.objects.get_or_create(title=title, text=text, url=url, display_url=display_url, bing_id=bing_id, human_created=False)
        if created:
            # Add as a child to the current topic
            # resource.save()
            topic.add_child_resource(resource)
        resources.append(resource)
    return resources 


    # Search bing api for topic title


    # TO DO - Implement algorithm to expand the right query using related topics and tfidif

    











''' LOGIN AUTHENTICATION VIEWS '''

def register(request):

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        user_form = SignupForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save(commit=False)

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors
            # Should render some kind of error

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = SignupForm()

    # Render the template depending on the context.
    return render(request,
            'registration/register.html',
            {'user_form': user_form, 'registered': registered} )


def user_login(request):

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            form = LoginForm(initial={'username':username})
            return render(request, 'registration/login.html', {'form':form})

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        form = LoginForm()
        return render(request, 'registration/login.html', {'form':form})




def fts(request):

    # watson.filter Returns model objects
    term = request.POST.get("q")
    if term is None: return None

    search_results = watson.filter(Resources, term)
    for obj in search_results:
        print obj.title # These are actual instances of `YourModel`, rather than `SearchEntry`.

    # watson.search returns SearchEntry objects
    # search_results = watson.search(term)
    # for result in search_results:
    #     print result.title, result.url

    out = [s.to_dict() for s in search_results]
    return HttpResponse(json.dumps(out))

