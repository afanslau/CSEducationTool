from bs4 import BeautifulSoup as Soup
from sodata.models import Resources, TopicRelations
from urllib import urlencode, urlopen
from django.core.management.base import BaseCommand

LOG_LEVEL_NONE = 0
LOG_LEVEL_INFO = 1
LOG_LEVEL_DEBUG = 2
LOG_LEVEL = LOG_LEVEL_INFO


k_cm_type_page = 'page'
k_cm_type_subcat = 'subcat'

#url string from dict	params = urllib.urlencode({})
stop_depth = 3
stop_width = 3 #Only get 10 children from each node

wikipedia_base_url = 'http://en.wikipedia.org%s'
page_preview_url = wikipedia_base_url % '/w/api.php?action=query&prop=extracts&format=xml&exintro&redirects&titles=%s'
subcategory_url = wikipedia_base_url % '/w/api.php?action=query&list=categorymembers&format=xml&cmprop=ids|title|type&cmtype=subcat&cmlimit=%d&cmtitle=%s'
wiki_url = wikipedia_base_url % '/wiki/%s'

class Command(BaseCommand):
	help = 'Loads wikipedia topics from the api'
	def handle(self, *args, **options):

		# **** REMOVE AFTER TESTING ****
		Resources.objects.all().delete()
		TopicRelations.objects.all().delete()

		testCategory = 'Category:Areas of computer science'
		depth = 0
		stop_depth = 3
		wiki_dfs(testCategory, depth, stop_depth)

#This gets both pages AND categories
def get_subpages(category_name, n):
	_url = subcategory_url % (n, category_name)
	soup = Soup(urlopen(_url))
	soup_page_title_list = soup.find_all('cm')
	if soup_page_title_list is None:
		print "soup cm tag is None"
		return []
	return [(cm['title'].encode('ascii','ignore'), cm['type']) for cm in soup_page_title_list]
	

def visit(title):

	''' 

	Get the page as-is 

	If there is no extract, try to split the category name and search for a page 

	'''
	apiurl = page_preview_url % title


	if LOG_LEVEL >= LOG_LEVEL_DEBUG:
		print('Fetching %s' % apiurl)


	#Try to get the page title - handles redirects?
	api_response_soup = Soup(urlopen(apiurl))
	page = api_response_soup.page
	if page.has_attr('missing'):
		#Page not found, return None
		return None, False
	returned_title = None if page is None or not page.has_attr('title') else page['title']
	



	# Split the Category title
	split_title = returned_title.split('Category:')
	if len(split_title) > 1:
		page_title = split_title[1]
	else:
		page_title = returned_title





	page_text = api_response_soup.find('extract').string

	print(page_title, page_text)

	if page_text is None or page_text == '':
		#Try to get the page with the same name, not the category 
		apiurl = page_preview_url % page_title
		api_response_soup = Soup(urlopen(apiurl))
		page = api_response_soup.page
		if not page.has_attr('missing'):
			#Page not found, just do nothing
			page_text = api_response_soup.find('extract').string
			

	else:
		page_text = page_text.string #HTML

	page_url = wiki_url % returned_title # Uses Category: if a corresponding page is not found on wikipedia
	#Create Topic object for this page
	topic, should_save = Resources.objects.get_or_create(title=page_title, pre_seeded=True)

	if topic.text is None: 
		topic.text=page_text
		should_save=True
	if topic.url is None: 
		topic.url=page_url
		should_save=True
	if should_save: 
		topic.save()
	return topic, should_save

def wiki_dfs(category_title, depth=0, stop_depth=0):
	#Create Topic object for this category_title

	topic, created = visit(category_title)


	#Evaluate stop condition  calling wiki_dfs('title') will default to one level deep search
	#Stop if we go too deep or hit a cycle
	if not created or depth > stop_depth:
		#Returns topic=None if the topic was not found
		return topic

	#iterate through the adjacent nodes
	width = 0
	sub_list = get_subpages(category_title, stop_width)


	for child_title, child_type in sub_list:
		is_category = child_type == k_cm_type_subcat
		#Check if it is a category 
		# split_title = child_title.split('Category:')
		# is_category = len(split_title) == 2
		# if len(split_title)>2:
		# 	raise ValueError("%s split into more than two pieces" % category_title)
		if LOG_LEVEL >= LOG_LEVEL_INFO:
			print 'Depth: %d  Width: %d  Visiting %s' % (depth, width, category_title)
	

		#if page - create topic for page
		if not is_category:
			#Request page from api for each page
			child_topic, child_created = visit(child_title)

		#if category
		if is_category:


			#Recursively traverse child nodes

			child_topic = wiki_dfs(child_title, depth+1, stop_depth)


			if LOG_LEVEL >= LOG_LEVEL_DEBUG:
				print ('Recursion returned to %s from %s' % (category_title, child_title))

		#Add the new child_resource or topic to  topic.child_resources
		if child_topic is not None:
			tr = TopicRelations(to_resource=child_topic, from_resource=topic)
			tr.save()

		width += 1
	#Return the created topic after all children have been created, added and traversed
	return topic 
