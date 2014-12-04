from django.shortcuts import render
from django.http import HttpResponse
from sodata.models import Topics, TopicRelations, Resources
import json

# Create your views here.

def index(request):
	#Get the top level objects
	topics = Topics.objects.filter(from_relation=None)
	data = {'topic':None, 'sub_topics':[{'id':topic.id,'title':topic.title} for topic in topics]}
	return render(request, 'sodata/index.html', data)

def topic_request(request):
	id = request.GET.get('id')
	try:
		parent = Topics.objects.get(id=id)
	except:
		return HttpResponseNotFound('<h1>Topic Not Found</h1>')
	topic_relation_ids = list(TopicRelations.objects.filter(from_node = parent).values_list('id',flat=True))
	topics = Topics.objects.filter(from_relation__in=topic_relation_ids)
	data = {'topic':parent,'sub_topics':[{'id':topic.id,'title':topic.title} for topic in topics]}
	return render(request, 'sodata/index.html', data)



def search_topics(request):
	term = request.GET.get('term')
	#Search database
	response_dict = {'results':['test result', term]}
	return HttpResponse(json.dumps(response_dict))

def create_subtopic(request):
	#Get the parent topic
	parent_id = request.GET.get('parent')


def create_topic_form(request):
	data = {}
	if 'id' in request.GET:
		id = request.GET.get('id')
		parent = Topics.objects.get(id=id)
		data['topic'] = parent
	return render(request, 'sodata/createTopic.html', data)


def save_topic_edits(request):
	print(request.POST)
	resources = json.loads(request.POST.get('resource-list'))
	for resource_input in resources:
		#Create and save a resource object
		Resources(text=resource_input)

	title = request.POST.get('title')
	print(title)
	# resources = request.POST.get('resource-list')
	# print(resources)
	
	t, created = Topics.objects.get_or_create(title=title)
	print(t, created)
	if created: t.save()
	return HttpResponse('created') if created else HttpResponse('already exists')

def submit_create_topic_form(request):
	#Get the attributes

	print(request.POST)
	return HttpResponse("<h2>Successfully submitted form!</h2><p>%s</p>" % str(request.POST))

