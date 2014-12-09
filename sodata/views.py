from django.shortcuts import render, render_to_response
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from sodata.models import TopicRelations, Resources
import json

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

	else:
		#Return one specific topic
		resource_id = int(resource_id)
		try:
			parent = Resources.objects.get(id=resource_id)
			topics = parent.get_child_resources()
			#Sort by updated_at
			if topics is not None:
				topics = sorted(topics, key=lambda t: t.updated_at, reverse=True)
			print('request - Render template with resource_id: %d  %s' % (parent.id, parent.title))
		except ObjectDoesNotExist:
			print('request - Render template with resource_id: %d  NOT FOUND' % resource_id)
			raise Http404
		
	data = {'topic':parent, 'resource_list':topics}
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
	new_resource = Resources(title=request.POST.get('title'), text=request.POST.get('text'), url=request.POST.get('url'))

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
		resource.title = new_title
		should_save = True

	new_text = request.POST.get('text')
	if new_text is not None:
		resource.text = new_text
		should_save = True

	new_url = request.POST.get('url')
	if new_url is not None:
		resource.url = new_url
		should_save = True

	if should_save: resource.save()

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

# def save_topic_edits(request):
# 	print(request.POST)
# 	resources = json.loads(request.POST.get('resource-list'))
# 	for resource_input in resources:
# 		#Create and save a resource object
# 		Resources(text=resource_input)

# 	title = request.POST.get('title')
	
# 	t, created = Topics.objects.get_or_create(title=title)
# 	print(t, created)
# 	if created: t.save()
# 	return json_response(t) if created else HttpResponse('Already exists')






# def submit_create_topic_form(request):
# 	#Get the attributes
# 	print(request.POST)
# 	return HttpResponse("<h2>Successfully submitted form!</h2><p>%s</p>" % str(request.POST))

