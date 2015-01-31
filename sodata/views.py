from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth import authenticate, login
from django.utils import timezone

from sodata.models import TopicRelations, Resources, UserRelation, UserActivity
from sodata.searchHelper import get_query
from sodata.forms import ResourceForm, SignupForm, LoginForm

import watson
from sodata.recommender import RecContext


import json, re 
import Bing
from bs4 import BeautifulSoup as Soup


ui_topic_base_url = 'resources/%d'

from sodata import TemplateDefaults

''' LOGIN AUTHENTICATION VIEWS '''
def ui_landing_page(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/resources")
    return render(request, 'sodata/landing.html')
def register(request):
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
            return user_login(HttpRequest(), registered=True)

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors
            # Should render some kind of error
    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = SignupForm()

    # Render the template depending on the context.
    return render(request,
            'registration/register.html',
            {'form': user_form} )
def user_login(request, registered=False):
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
        return render(request, 'registration/login.html', {'form':form, 'registered':registered})

''' GET /resources  '''
def ui_get_resource(request, resource_id=None):
    data = get_resource(request, resource_id)
    return render(request,'sodata/topic.html', data) #same-as  render(request, 'sodata/index.html', data)
def get_resource(request, resource_id=None):

    #Default for anon users
    parent = None
    user_relation = None 
    user_relations = {}
    recommended_resources = None
    recommended_relations = None


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

    rec_data = api_recommend_resources(request, resource_id=parent.id)
    recommended_resources = rec_data["resource_list"]
    recommended_relations = rec_data["user_relations"]


    data = {'new_resource_form':new_resource_form,  #base.html
            'resource':parent,  #base.html
            'user_relation':user_relation,  #topic.html
            'resource_list':topics, 
            'user_relations':user_relations, 
            'recommended_resources':recommended_resources, 
            'recommended_relations':recommended_relations
        }
    return data
def api_get_resource(request, resource_id):
    resource_id = int(resource_id)
    try:
        resource = Resources.objects.get(id=resource_id)
    except ObjectDoesNotExist:
        raise Http404

    print('request - GET resource id:%d  %s' % (resource_id, resource.title))
    return json_response(resource)

""" CREATE /resources """
def api_create_resource(request, parent_id=None):
    resource = create_resource(request, parent_id)
    if type(resource) is Resources:
        return json_response(resource)
    elif type(resource) is ResourceForm:
        return resource.errors.as_data()
    else:
        return HttpResponse("There was an error processing the create_resource request")
def ui_create_resource(request, parent_id=None):
    print 'ui_create_resource',request.POST
    pid = int(parent_id) if parent_id is not None else None  # I think this is unnecessary. Check when there is time and if so remove
    new_resource = create_resource(request, pid)

    if type(new_resource) is Resources:
        rid = request.POST.get("current_resource_id")

        print 'ui_create_resource ', rid

        if rid is None:
            _url = '/resources/%s' % parent_id if parent_id is not None else '/'
        else:
            _url = '/resources/%s' % rid

        return HttpResponseRedirect(_url)
    elif type(new_resource) is ResourceForm:
        try:
            parent = Resources.objects.get(id=parent_id)
        except Exception, e:
            parent = None
            print 'ui_create_resource   Exception caught: ', e
        return render(request, 'sodata/new_resource_form_container.html', {'new_resource_form':new_resource, 'resource':parent})
def create_resource(request, parent_id=None):

    if request.method=="POST":
        form = ResourceForm(data={'title':request.POST.get('title'), 'text':request.POST.get('text'), 'url':request.POST.get('url')})

        if form.is_valid():
            cd = form.cleaned_data
            new_resource = form.save(commit=False)
    
    # new_resource = Resources(title=request.POST.get('title'), text=request.POST.get('text'), url=request.POST.get('url'))
            if request.user.is_authenticated():
                try:
                    if parent_id is not None:
                        parent = Resources.objects.get(id=parent_id)
                    else:
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
            return form 
            
""" UPDATE /resources """
def api_update_resource(request, resource_id=None):
    if resource_id is None: raise Http404
    updated_resource = update_resource(request, resource_id)
    if update_resource is None:
        return HttpResponse("You do not have permission to edit this resource", status=401)    
    return json_response(updated_resource)
def ui_update_resource(request, resource_id=None):
    if resource_id is None: raise Http404

    if request.method == "POST":
        updated_resource = update_resource(request, resource_id)
        if update_resource is None:
            return HttpResponse("You do not have permission to edit this resource", status=401)
        return HttpResponseRedirect('/resources/%s'%resource_id)
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


    if request.user.is_authenticated() and resource.can_edit(request.user):
        # data = {'title':request.POST.get('title'), 'text':request.POST.get('text'), 'url': request.POST.get('url')}
        form = ResourceForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
        return resource
    else:
        return None

    # # Update the content
    # should_save = False
    # new_title = request.POST.get('title')
    # if new_title is not None:
    #     resource.title = new_title if new_title != '' else None
    #     should_save = True

    # new_text = request.POST.get('text')

    # # parsed_urls = []
    # # if request.POST.get('text') is not None and request.POST.get('url') is None:
    # #     parsed_urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', request.POST.get('text'))
    # #     print(parsed_urls)
    # if new_text is not None:
    #     resource.text = new_text if new_text != '' else None
    #     should_save = True

    # new_url = request.POST.get('url')
    # if len(parsed_urls)>0 and (new_url is None or new_url == ''):
    #     new_url = parsed_urls[0]

    # # new_url = request.POST.get('url')
    # if new_url is not None:
    #     resource.url = new_url if new_url != '' else None
    #     should_save = True

    # if should_save: resource.save()
    # return resource

""" STAR / UNSTAR """
def api_star_resource(request, resource_id=None):
    rating = 1
    return json_response(rate_resource(request, resource_id=resource_id, rating=rating))
def api_unstar_resource(request, resource_id=None):
    rating = 0
    return json_response(rate_resource(request, resource_id=resource_id, rating=rating))
def api_rate_resource(request, resource_id=None, rating=0):
    r = json_response(rate_resource(request, resource_id=resource_id, rating=rating))    
    return r
def rate_resource(request, resource_id=None, rating=0):
    print "rate_resource ", request.user.username, resource_id, rating>=1
    if request.user.is_authenticated():    
        try: 
            ur, created = UserRelation.objects.get_or_create(resource__id=resource_id, user=request.user)
        except ObjectDoesNotExist:
            raise Http404
        ur.starred = rating>=1
        ur.save()
        return ur.resource
    else: 
        return None

""" DELETE /resources """
def ui_delete_resource(request, resource_id=None):
    if resource_id is None: raise Http404

    try:
        to_delete = Resources.objects.get(id=resource_id)
    except ObjectDoesNotExist:
        print 'ui_delete_resource  object not found with id ', resource_id
        raise Http404

    # Once the resource is deleted, redirect to home.
    if request.user.is_authenticated() and to_delete.can_edit(request.user):
        to_delete.delete()
        return HttpResponseRedirect('/resources')
    else:
        return HttpResponseRedirect('/resources/%s' % resource_id)
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
    if request.user.is_authenticated() and to_delete.can_edit(request.user):
        to_delete.delete()
    else:
        # Suggest a delete
        suggest_delete(request, resource_id)

    print('request - DELETE resource %d  %s' % (resource_id, to_delete.title))
    
    return json_response(to_delete)





""" RELATE """
# @login_required  Look up how to use this, need to decide on a redirect strategy
def api_create_relation(request, parent_id=None, child_id=None):

    relation = create_relation(request, parent_id, child_id)
    if relation is None:
        return HttpResponse("You must be logged in to create a relation", status=401)
    return HttpResponse(json.dumps(relation.to_dict()))
def ui_create_relation(request, parent_id=None, child_id=None):
    create_relation(request, parent_id, child_id)
    return HttpResponseRedirect('/resources/%s'%parent_id)
def create_relation(request, parent_id, child_id):
    if not request.user.is_authenticated():
        return None
    try:
        if parent_id is None:
            # Get home
            parent = Resources.objects.get(author=request.user, is_home=True)
        else:
            parent = Resources.objects.get(id=parent_id)
        
        child = Resources.objects.get(id=child_id)
        relation, created = TopicRelations.objects.get_or_create(from_resource=parent, to_resource=child, perspective_user=request.user)
        # I think this performs the save automatically
        return relation
    except ObjectDoesNotExist:
        print('request - CREATE relation from %d to %d  NOT FOUND' % (parent_id, child_id))
        raise Http404
    print('request - CREATE relation from %d %s to %d %s ' % (relation.from_resource.id, relation.from_resource.title, relation.to_resource.id, relation.to_resource.title))



def ui_choose_parent_pin_to(request, resource_id=None):
    print 'ui_choose_parent_pin_to  ', resource_id
    try:
        r = Resources.objects.get(id=resource_id)
    except ObjectDoesNotExist:
        return Http404
    search_results = watson.search(r.title)
    data = {'resource_id':r.id, 'title':r.title, 'resource_list':search_results.values('object_id_int','title')} # return only title and id for speed
    return render(request, 'sodata/pin_to_topic.html', data)
def ui_autocomplete_search(request):
    term = request.GET.get("q")
    search_results = watson.search(term).values('object_id_int','title')
    data = {'resource_list':search_results}
    return render(request, 'sodata/title-items.html', data)




def api_delete_relation_by_id(request, relation_id):
    try:
        to_delete = TopicRelations.objects.get(id=relation_id)
    except ObjectDoesNotExist:
        print('request - DELETE relation_id: %d NOT FOUND' % relation_id)
        raise Http404
    print('request - DELETE relation from %s to %s' % (to_delete.from_resource.title, to_delete.to_resource.title))
    to_delete.delete()
    return json_response(to_delete)
def api_delete_relation_by_resources(request, parent_id, child_id):
    if request.user.is_authenticated():
        try:
            to_delete = TopicRelations.objects.get(from_resource=parent_id, to_resource=child_id)
        except ObjectDoesNotExist:
            # print('request - DELETE relation from %d to %d NOT FOUND' % (parent_id, child_id))
            raise Http404
        print('request - DELETE relation from %s to %s' % (to_delete.from_resource.title, to_delete.to_resource.title))
        to_delete.delete()
        return json_response(to_delete)
    else:
        return HttpResponse("You must be logged in to delete a relation", status=401)
def ui_delete_relation_by_resources(request, parent_id, child_id):
    api_delete_relation_by_resources(request, parent_id, child_id)
    return HttpResponseRedirect('/resources/%s'%parent_id)





""" SEARCH & RECOMMEND """
# Search
def ui_search_resources(request):

    # watson.filter Returns model objects
    term = request.GET.get("q")

    if request.GET.get('simple_search'):
        search_results = watson.search(term, models=(Resources,))
        return HttpResponse(json.dumps([{"title":r.title, "id":r.object_id_int} for r in search_results]))
    

    search_results = watson.filter(Resources, term)
    user_relations = {}
    if request.user.is_authenticated():
        user_relations = UserRelation.get_relations_by_resource_id(request, search_results)
        # urs = UserRelation.objects.filter(user=request.user, resource__in=search_results)
        # for r in search_results:
        #     ur, created = urs.get_or_create(resource=r, user=request.user)
        #     if created: ur.save()
        #     user_relations[r.id] = ur

    print TemplateDefaults.base['new_resource_form']
    data = {'new_resource_form':TemplateDefaults.base['new_resource_form'],
            'resource':None,
            'resource_list':search_results, 
            'user_relations':user_relations,
            'query': term
            }



    if request.GET.get("format") == 'json':
        return HttpResponse(json.dumps(data))

    return render(request, 'sodata/search_results.html', data)
def api_search_resources(request):
    q = request.POST.get('q')
    return HttpResponse(json.dumps([ r.to_dict() for r in watson.filter(Resources, q)]))
# UserActivity
def suggest_delete(request, resource_id):
    REMOVED_RELATION = 2 # Should be imported from a constants file...
    u = None
    if request.user.is_authenticated():
        u = request.user
    UserActivity.objects.create(user=u, resource=resource_id, activity_type=REMOVED_RELATION)
 
# GET recommended
# TO DO - Implement algorithm to expand the right query using related topics and tfidif
def get_recommended(request, resource=None):
    if resource is None:
        return None

    context = RecContext(request.user, resource)
    return context.recommend()
def ui_recommend_resources(request, resource_id=None):
    data = api_recommend_resources(request, resource_id)
    if data is None:
        raise Http404
    return render(request, 'sodata/paginated.html', data)
def api_recommend_resources(request, resource_id=None):
    if resource_id is None:
        raise Http404

    try:
        resource = Resources.objects.get(id=resource_id)
    except ObjectDoesNotExist:
        raise Http404  # I think this might be the default error for ObjectDoesNotExist


    full_resource_list = get_recommended(request, resource)
    page_number = request.GET.get('page')
    paginator = Paginator(full_resource_list, 3) # Show 3 contacts per page



    try:
        resource_list = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        resource_list = paginator.page(1)
        page_number = 1
    except EmptyPage:
        return None


    user_relations = UserRelation.get_relations_by_resource_id(request, resource_list)
    return {"resource_list":resource_list,
            "user_relations":user_relations,
            "page_number":page_number
            }


''' Helper function - render a json response for a given resource '''
def json_response(resource):
    if resource is None: raise Http404
    try: # make a list of json serializable dictionaries 
        out = [r.to_dict() for r in resource]
    except TypeError: #resource is one resource.. Not iterable
        out = resource.to_dict()
    return HttpResponse(json.dumps(out))







