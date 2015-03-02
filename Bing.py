import urllib, urllib2, base64
from bs4 import BeautifulSoup as Soup 
from django.db.models import Count, Sum

from CSEducationTool.settings import BING_USERNAME, BING_PASSWORD, BING_API_BASE

#To move to settings.py
# BING_API_BASE = "https://api.datamarket.azure.com/Bing/"
# BING_USERNAME = 'afanslau@gmail.com'
# BING_PASSWORD = 'aPA1Hr8rGzCUyPMCEpxFOFWfpHLL0RvisEFc1Q+mJsE'

search_add_ons = ['tutorial','example','getting started','learning','how to','essentials']
def gather_resources(n_resources_per_tag=3):
	
	# Fetch the most interacted with resources
	Resources.objects.annotate(num_children=Sum('child_resources__confidence')).order_by('-num_children')




#Returns api response as a string
def perform_query(query_term, skip=0, top=4):
	clean_query = query_term.replace("'", '')
	clean_query = "'%s'" % clean_query

	url_end = "Search/v1/Web?%s" % urllib.urlencode({"Query":clean_query, "$skip":skip, "$top":top})
	request = urllib2.Request(BING_API_BASE + url_end)
	
	# You need the replace to handle encodestring adding a trailing newline 
	# (https://docs.python.org/2/library/base64.html#base64.encodestring)
	base64string = base64.encodestring('%s:%s' % (BING_USERNAME, BING_PASSWORD)).replace('\n', '')
	request.add_header("Authorization", "Basic %s" % base64string)   

	print "Searching Bing for   %s" % clean_query
	print request.get_full_url()

	#Check cache? Am I legally allowed to do that? Probably not...

	result = urllib2.urlopen(request)
	return result.read()



'''
xml  feed/entry list
entry/content/title, description, displayurl, url
'''