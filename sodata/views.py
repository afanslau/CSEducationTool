from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth import authenticate, login
from django.utils import timezone

from sodata.models import TopicRelations, Resources, UserRelation, UserActivity
from sodata.searchHelper import get_query
from sodata.forms import ResourceForm, SignupForm, LoginForm

import watson


import json, re 
import Bing
from bs4 import BeautifulSoup as Soup


ui_topic_base_url = 'resources/%d'

''' Render and return the topic template page '''
def ui_get_resource(request, resource_id=None):
    data = get_resource(request, resource_id)
    return render(request,'sodata/newtopic.html', data) #same-as  render(request, 'sodata/index.html', data)

def get_resource(request, resource_id=None):

    #Default for anon users
    parent = None
    user_relation = None 
    user_relations = {}
    external_search_results = None


    if resource_id is None:
        #Return top level topics
        if request.user.is_authenticated():
            parent = Resources.objects.get(author=request.user, is_home=True)
        else:
            # Parent is fake, just for display purposes. This probably has to change
            parent = Resources(title='Home',text='Hello World. Add your favorite resources, create topics and get recommendations')

    else:
        #Return one specific topic
        resource_id = int(resource_id)
        try:
            parent = Resources.objects.get(id=resource_id)
        except ObjectDoesNotExist:
            print('request - Render template with resource_id: %d  NOT FOUND' % resource_id)
            raise Http404

    #Get the sub-resources where user_perspective=None (public) or is the logged in user
    # topics = Resources.objects.filter(parent_resources__from_resource=parent).select_related('user_relations')
    if request.user.is_authenticated():
        relations = TopicRelations.objects.filter(Q(perspective_user=request.user)|Q(perspective_user__isnull=True), from_resource=parent).select_related('to_resource')
    else:
        relations = TopicRelations.objects.filter(perspective_user__isnull=True, from_resource=parent).select_related('to_resource')
    topics = [r.to_resource for r in relations]

    # When the UI requests a resource, update the logged in user's UserRelation
    if request.user.is_authenticated():
        user_relation, created = UserRelation.objects.get_or_create(resource=parent, user=request.user)
        # Update the user visits
        user_relation.num_visits += 1
        user_relation.last_visited = timezone.now()
        user_relation.save()

        user_relations = UserRelation.get_relations_by_resource_id(request, topics)
        # Get children UserRelation
        # urs = UserRelation.objects.filter(user=request.user, resource__in=topics)
        # for r in topics:
        #     ur,created = urs.get_or_create(user=request.user, resource=r)
        #     if created: ur.save()
        #     user_relations[r.id] = ur

    #Sort by updated_at
    if topics is not None:
        topics = sorted(topics, key=lambda t: t.updated_at, reverse=True)
    if parent.id is not None:
        print('request - Render template with resource_id: %d  %s' % (parent.id, parent.title))
        

    # Other return data
    new_resource_form = ResourceForm()
    external_search_results = get_external_search(topic=parent)


    data = {'new_resource_form':new_resource_form,  #base.html
            'resource':parent,  #base.html
            'user_relation':user_relation,  
            'resource_list':topics, 
            'user_relations':user_relations, 
            'external_search_results':external_search_results, 
            # 'user':request.user, 
            
        }
    return data


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
    return HttpResponse("Search not Implemented")


def api_search_resources(request):
    q = request.GET.get('q')
    print ('request - search resources for q= %s' % q)
    return HttpResponse('Not Implemented')



''' POST /resources/{id}/create - create a resource in the given topic '''
''' POST /resources/create - create a stand-alone resource '''
def api_create_resource(request, parent_id=None):
    resource = create_resource(request, parent_id)
    if resource is not None:
        return json_response(resource)
    else:
        return HttpResponseBadRequest("Invalid Form Data")

def ui_create_resource(request, parent_id=None):
    print 'ui_create_resource',request.POST
    pid = int(parent_id) if parent_id is not None else None
    new_resource = create_resource(request, pid)

    if new_resource is not None:
        rid = request.POST.get("current_resource_id")

        print 'ui_create_resource ', rid

        if rid is None:
            _url = '/resources/%s' % parent_id if parent_id is not None else '/'
        else:
            _url = '/resources/%s' % rid

        return HttpResponseRedirect(_url)
    else:
        return HttpResponseBadRequest("Invalid Form Data")

def create_resource(request, parent_id=None):

    if request.method=="POST":
        form = ResourceForm(data={'title':request.POST.get('title'), 'text':request.POST.get('text'), 'url':request.POST.get('url')})

        if form.is_valid():
            cd = form.cleaned_data

            print 'form is valid ', cd 

            new_resource = form.save(commit=False)
    
    # new_resource = Resources(title=request.POST.get('title'), text=request.POST.get('text'), url=request.POST.get('url'))
            if request.user.is_authenticated():
                try:
                    if parent_id is not None:
                        parent = Resources.objects.get(id=parent_id)
                    else:

                        print 'create_resource in home'

                        parent = Resources.objects.get(is_home=True, author=request.user) # Get the user's home page
                    print('request - CREATE resource under %s with data %s' % (parent.title, new_resource.to_dict()))
                except ObjectDoesNotExist:
                    print('request - CREATE resource under %d  NOT FOUND' % parent_id)
                    raise Http404
                new_resource.author = request.user
                new_resource.save()
                
                tr = TopicRelations(from_resource=parent, to_resource=new_resource)
                # If the user is the author, leave perspective_user as None
                if request.user != parent.author:
                     tr.perspective_user = request.user 
                tr.save()

                UserRelation.objects.create(user=request.user, resource=new_resource, user_type=1) #AUTHOR
                UserActivity.objects.create(user=request.user, resource=new_resource, activity_type=3) #CREATED
            else:
                new_resource.save()
            return new_resource
        else:
            print 'Form was invalid ', form.errors, form.non_field_errors()
            

def api_update_resource(request, resource_id=None):
    if resource_id is None: raise Http404
    updated_resource = update_resource(request, resource_id)
    return json_response(updated_resource)

def ui_update_resource(request, resource_id=None):
    if resource_id is None: raise Http404

    if request.method == "POST":
        updated_resource = update_resource(request, resource_id)
        return ui_get_resource(request, resource_id)
    else: 
        data = get_resource(request, resource_id)
        data['form'] = ResourceForm(data['resource'].to_dict())
        return render(request,'sodata/edittopic.html', data)

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


def api_star_resource(request, resource_id=None):
    rating = 1
    return json_response(rate_resource(request, resource_id=resource_id, rating=rating))
def api_unstar_resource(request, resource_id=None):
    rating = 0
    return json_response(rate_resource(request, resource_id=resource_id, rating=rating))

def api_rate_resource(request, resource_id=None, rating=0):
    return json_response(rate_resource(request, resource_id=resource_id, rating=rating))    
    
def rate_resource(request, resource_id=None, rating=0):

    print "rate_resource ", request.user.username, resource_id, rating>=1

    if request.user.is_authenticated():    
        try: 
            ur = UserRelation.objects.get(resource__id=resource_id, user=request.user)
        except ObjectDoesNotExist:
            raise Http404
        ur.starred = rating>=1
        ur.save()
        return ur.resource
    else: 
        return None



def api_delete_resource(request, resource_id=None):
    if resource_id is None: return HttpResponse()
    resource_id = int(resource_id)
    print('request - Delete %d' % resource_id)
    try:
        to_delete = Resources.objects.get(id=resource_id)
    except ObjectDoesNotExist:
        print('request - DELETE resource %d  NOT FOUND' % resource_id)
        raise Http404

    # Only the author can delete a resource
    if request.user.is_authenticated() and request.user == to_delete.author:
        to_delete.delete()
    else:
        # Suggest a delete
        suggest_delete(request, resource_id)

    print('request - DELETE resource %d  %s' % (resource_id, to_delete.title))
    
    return json_response(to_delete)

def suggest_delete(request, resource_id):
    REMOVED_RELATION = 2 # Should be imported from a constants file...
    u = None
    if request.user.is_authenticated():
        u = request.user
    UserActivity.objects.create(user=u, resource=resource_id, activity_type=REMOVED_RELATION)
    




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

            #Create the users home page resource
            Resources.create_home(user)

            #If needed, create a UserProfie object

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, user_form.errors
            # Should render some kind of error

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = SignupForm()

    # Render the template depending on the context.
    return render(request,
            'registration/register.html',
            {'form': user_form, 'registered': registered} )


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




def search_view(request):

    # watson.filter Returns model objects
    term = request.GET.get("q")
    search_results = watson.filter(Resources, term)
    user_relations = {}
    if request.user.is_authenticated():
        user_relations = UserRelation.get_relations_by_resource_id(request, topics)
        # urs = UserRelation.objects.filter(user=request.user, resource__in=search_results)
        # for r in search_results:
        #     ur, created = urs.get_or_create(resource=r, user=request.user)
        #     if created: ur.save()
        #     user_relations[r.id] = ur

    data = {'resource_list':search_results, 
            'user_relations':user_relations,
            'query': term
            }
    return render(request, 'sodata/search_results.html', data)



def ui_recommend_resources(request, resource_id=None):
    
    if resource_id is None:
        raise Http404

    try:
        resource = Resources.objects.get(id=resource_id)
    except ObjectDoesNotExist:
        raise Http404  # I think this might be the default error for ObjectDoesNotExist


    full_resource_list = watson.filter(Resources, resource.title)   # Put recommended choice algorithm here    
    page_number = request.GET.get('page')
    paginator = Paginator(full_resource_list, 3) # Show 3 contacts per page

    try:
        resource_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        resource_list = paginator.page(1)
        page_number = 1
    except EmptyPage:
        return HttpResponse("")

    user_relations = UserRelation.get_relations_by_resource_id(request, resource_list)

    data = {"resource_list":resource_list,
            "user_relations":user_relations,
            "page_number":page_number
            }
    return render(request, 'sodata/paginated.html', data)
