from bs4 import BeautifulSoup as Soup
from sodata.models import Resources, TopicRelations, UserRelation
from django.contrib.auth.models import User
from urllib import urlencode, urlopen
from django.core.management.base import BaseCommand
# from sodata.learning import store_vectors

LOG_LEVEL_SILENT = -1
LOG_LEVEL_ERROR = 0
LOG_LEVEL_INFO = 1
LOG_LEVEL_DEBUG = 2
LOG_LEVEL = LOG_LEVEL_INFO


k_cm_type_page = 'page'
k_cm_type_subcat = 'subcat'

#url string from dict	params = urllib.urlencode({})
stop_depth = 2
stop_width = None #Only get 10 children from each node
top_level_width = 0  # Used only for debugging and progress logging purposes

wikipedia_base_url = 'http://en.wikipedia.org%s'
page_preview_url = wikipedia_base_url % '/w/api.php?action=query&prop=extracts&format=xml&exintro&redirects&titles=%s'
subcategory_url = wikipedia_base_url % '/w/api.php?action=query&list=categorymembers&format=xml&cmprop=ids|title|type&cmtype=subcat&cmlimit=%d&cmtitle=%s'
wiki_url = wikipedia_base_url % '/wiki/%s'


system_user, created = User.objects.get_or_create(username='System')
Resources.create_home(system_user)

class Command(BaseCommand):
	help = 'Loads wikipedia topics from the api'
	def handle(self, *args, **options):

		# **** REMOVE AFTER TESTING ****
		# Resources.objects.filter(author=system_user, is_home=False).delete()
		# UserRelation.objects.all().delete()
		# TopicRelations.objects.all().delete()

		testCategory = 'Category:Areas of computer science'
		depth = 0
		wiki_dfs(category_title=testCategory, depth=depth, stop_depth=stop_depth, top_level_width=top_level_width)
		# store_vectors()

#This gets both pages AND categories
def get_subpages(category_name, n_subpages):
	# If n is None, get all subpages
	if n_subpages is None:
		n_subpages = 100
	_url = subcategory_url % (n_subpages, category_name)

	soup = Soup(urlopen(_url))
	soup_page_title_list = soup.find_all('cm')
	if soup_page_title_list is None:
		if LOG_LEVEL >= LOG_LEVEL_ERROR:
			print "get_subpages ERROR: soup cm tag is None"
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



	page_text = api_response_soup.find('extract').get_text()
	if page_text is None: # or page_text == '':
		#Try to get the page with the same name, not the category 
		apiurl = page_preview_url % page_title
		api_response_soup = Soup(urlopen(apiurl))
		page = api_response_soup.page
		if not page.has_attr('missing'):
			#Page not found, just do nothing
			page_text = api_response_soup.find('extract').get_text()
			

	else:
		page_text = page_text.get_text() #HTML

	page_url = wiki_url % returned_title # Uses Category: if a corresponding page is not found on wikipedia
	


	#Create Topic object for this page

	topic, should_save = Resources.objects.get_or_create(title=page_title, pre_seeded=True, author=system_user)
	UserRelation.objects.get_or_create(user=system_user, resource=topic)

	# Take away wikipedia ending
	wikiending = ' - Wikipedia, the free encyclopedia'
	if page_title.endswith(wikiending):
		page_title = page_title[:-len(wikiending)]
		topic.title = page_title
		should_save=True 

	if topic.text is None: 
		topic.text=page_text
		should_save=True
	if topic.url is None: 
		topic.url=page_url
		should_save=True
	if should_save: 
		topic.save()
	return topic, should_save

def wiki_dfs(category_title, depth=0, stop_depth=0, path=None, top_level_width=None):
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


	

		#if page - create topic for page
		if not is_category:
			#Request page from api for each page
			child_topic, child_created = visit(child_title)

		#if category
		if is_category:


			#Recursively traverse child nodes
			new_top_level_width = top_level_width
			if depth == 0: 
				new_top_level_width += 1
				if LOG_LEVEL >= LOG_LEVEL_INFO:
					print('Reached top level width of '+str(new_top_level_width))
				

			width += 1
			sep = ''
			newpath = path
			if newpath is None: 
				newpath = ''
			else: 
				sep = '-'
			newpath += sep+str(width)
			if LOG_LEVEL >= LOG_LEVEL_INFO:
				print 'Path: %s  Visited %s  depth: %d stop_depth: %d' % (newpath, child_title, depth, stop_depth)


			child_topic = wiki_dfs(child_title, depth+1, stop_depth, top_level_width=new_top_level_width, path=newpath)

			
			if LOG_LEVEL >= LOG_LEVEL_DEBUG:
				print ('Recursion returned to %s from %s' % (category_title, child_title))




		#Add the new child_resource or topic to  topic.child_resources
		if child_topic is not None:
			TopicRelations.objects.create(to_resource=child_topic, from_resource=topic, perspective_user=system_user)

		
	#Return the created topic after all children have been created, added and traversed
	return topic 
