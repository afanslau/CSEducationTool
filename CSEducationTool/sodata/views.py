from django.shortcuts import render
from django.http import HttpResponse
import json

# Create your views here.

def index(request):
	return render(request, 'sodata/index.html')

def search_topics(request):
	print request.GET
	term = request.GET.get('term')
	#Search database

	response_dict = {'results':['test result', term]}
	return HttpResponse(json.dumps(response_dict))

