from django.shortcuts import render, render_to_response
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from sodata.models import TopicRelations, Resources
from sodata.searchHelper import get_query
import json, re 

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
		#Return top level resources

		# Parent is fake, just for display purposes. This is a bad way to do this, violates MVC
		parent = Resources(title='Home',text='This is a website where you can explore computer science topics. You can store good resources you find, and share them with others.')
		resources = Resources.objects.filter(parent_resources=None)
		resources = sorted(resources, key=lambda t: t.title, reverse=True)
		plist = []

	else:
		#Return one specific topic
		resource_id = int(resource_id)
		try:
			parent = Resources.objects.get(id=resource_id)
			resources = parent.get_child_resources()
			plist = parent.get_parent_resources()
			#Sort by updated_at
			if resources is not None:
				resources = sorted(resources, key=lambda t: t.title) # , reverse=True)
			print('request - Render template with resource_id: %d  %s' % (parent.id, parent.title))
		except ObjectDoesNotExist:
			print('request - Render template with resource_id: %d  NOT FOUND' % resource_id)
			raise Http404

	data = {'topic':parent, 'resource_list':resources, 'parent_list':plist}
	return render_to_response('sodata/topic.html', data) #same-as  render(request, 'sodata/index.html', data)


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

	parsed_urls = []
	if request.POST.get('text') is not None and request.POST.get('url') is None:
		parsed_urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', request.POST.get('text'))
		print(parsed_urls)

	new_url = request.POST.get('url')
	if len(parsed_urls)>0 and (new_url is None or new_url == ''):
		new_url = parsed_urls[0]

	
	new_resource = Resources(title=request.POST.get('title'), text=request.POST.get('text'), url=new_url)

	# new_resource.save()

	if parent_id is None:
		print(new_resource.id)
		new_resource.save()
		print(new_resource.id)
		print('request - CREATE resource with data %s' % request.POST)
	else:
		try:
			parent_id = int(parent_id)
			parent = Resources.objects.get(id=parent_id)
		except ObjectDoesNotExist:
			print('request - CREATE resource under %d  NOT FOUND' % parent_id)
			raise Http404
		print(new_resource.id)
		new_resource.save()
		print(new_resource.id)
		TopicRelations(from_resource=parent, to_resource=new_resource).save()
		print('request - CREATE resource under %s with data %s' % (parent.title, new_resource.to_dict()))

	print(new_resource.to_dict())
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
	relation, created = TopicRelations.objects.get_or_create(from_resource=parent, to_resource=child)
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























# def index(request):
# 	#Get the top level objects
# 	home_parent = Resources(title='This is the home page',text='This is a website where you can explore computer science topics. You can store good resources you find, and share them with others.')
# 	topics = Resources.objects.filter(parent_resources=None)

# 	print( topics.values_list('title','text','url') )

# 	data = {'topic':home_parent, 'resource_list':topics}
# 	return render_to_response('sodata/index.html', data) #render(request, 'sodata/index.html', data)




# def topic_request(request):
# 	id = request.GET.get('id')
# 	try:
# 		parent = Resources.objects.get(id=id)
# 	except:
# 		return HttpResponseNotFound('<h1>Topic Not Found</h1>')
# 	# topic_relation_ids = list(TopicRelations.objects.filter(from_resource = parent).values_list('id',flat=True))
# 	topics = parent.get_child_resources()  # Resources.objects.filter(from_relation__in=topic_relation_ids)
# 	data = {'topic':parent,'sub_topics':[{'id':topic.id,'title':topic.title} for topic in topics]}
# 	return render(request, 'sodata/index.html', data)



# def search_topics(request):
# 	term = request.GET.get('term')
# 	#Search database
# 	response_dict = {'results':['test result', term]}
# 	return HttpResponse(json.dumps(response_dict))

# def create_subtopic(request):
# 	#Get the parent topic
# 	parent_id = request.GET.get('parent')


# def create_topic_form(request):
# 	data = {}
# 	if 'id' in request.GET:
# 		id = request.GET.get('id')
# 		parent = Resources.objects.get(id=id)
# 		data['topic'] = parent
# 	return render(request, 'sodata/createTopic.html', data)


# def save_resource(request):
# 	print(request.POST)

# 	resource = Resources(title=request.POST.get('title'), text=request.POST.get('text'), url=request.POST.get('url'))
# 	data = {'resource':resource}
# 	return render(request, 'sodata/list_item.html', data)




# def submit_create_topic_form(request):
# 	#Get the attributes
# 	print(request.POST)
# 	return HttpResponse("<h2>Successfully submitted form!</h2><p>%s</p>" % str(request.POST))

