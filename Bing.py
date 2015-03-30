import urllib, urllib2, base64
from bs4 import BeautifulSoup as Soup 
from django.db.models import Count, Sum
from sodata.models import Resources
from sodata.models import get_bing_user
from django.conf import settings



#To move to settings.py
BING_API_BASE = settings.BING_API_BASE
BING_USERNAME = settings.BING_USERNAME
BING_PASSWORD = settings.BING_PASSWORD

bing_user = get_bing_user()

search_add_ons = ['tutorial','example','getting started','learning','how to','essentials']
def gather_resources(n_resources_per_tag=3):
	
	# Fetch the most interacted with resources
	Resources.objects.annotate(num_children=Sum('child_resources__confidence')).order_by('-num_children')


# Make this better
def get_resources_for_query(query_term, top=5, skip=0, max=15):
	res = perform_query(query_term,top,skip)
	soup = Soup(res)
	entries = soup.feed.find_all('entry')

	print 'get_resources_for_query   len(entries) = ', len(entries)

	return [get_resource_for_bing_entry(entry) for entry in entries]


def get_resource_for_bing_entry(entry):
	# try:
		url = entry.content.find('d:url').get_text()
		new, created = Resources.objects.get_or_create(url=url)
		if created:
			new.title = entry.content.find('d:title').get_text()	
			new.displayurl = entry.content.find('d:displayurl').get_text()
			new.text = entry.content.find('d:description').get_text()
			new.author = bing_user
		

		return new
	# except Exception:
	# 	print 'could not get resource from ', str(entry)[:140]
	# 	return None
	






#Returns api response as a string
def perform_query(query_term, top=5, skip=0):
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
 
	return result



'''
xml  feed/entry list
entry/content/title, description, displayurl, url
'''