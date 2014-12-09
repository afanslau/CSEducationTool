
'''

Get cs category

create topic(title=cs, url = wikipedia/cs, description = content[:first p tag or first n complete sentances])

parse out sub-topics and resources

For each su


'''


from bs4 import BeautifulSoup as Soup
from sodata.models import Topics 
import urllib

#url string from dict	params = urllib.urlencode({})
stop_depth = 10
wikipedia_base_url = 'http://en.wikipedia.org%s'
subcategory_url = wikipedia_base_url % '/w/api.php?action=query&list=categorymembers&prop=extracts&format=xml&cmtitle=%s'
page_preview_url = wikipedia_base_url % '/w/api.php?action=query&prop=extracts&format=xml&exintro=&titles=%s'
category_query_url = wikipedia_base_url % 'http://en.wikipedia.org/w/index.php?action=submit&title=Special:Export&addcat&catname=%s'
wiki_url = wikipedia_base_url % '/wiki/%s'


#This gets both pages AND categories
def scrapeCategoryPages(category_name):
	_url = category_query_base_url % category_name
	soup = Soup(urllib.urlopen(_url))
	page_title_list = soup.textarea.string.split('\n')
	return page_title_list

def visit(child_title):
	wikipedia_api_response_soup = Soup(urllib.urlopen(wikipedia_api_base_url % child_title))
	child_text = wikipedia_api_response_soup.rev.string  #HTML
	child_url = wiki_url % child_title
	#Create Topic object for this page
	child_topic, should_save = Topics.objects.get_or_create(title=child_title)
	if child_topic.text is None: 
		child_topic.text=child_text
		should_save=True
	if child_topic.url is None: 
		child_topic.url=child_url
		should_save=True
	if should_save: 
		child_topic.save()
	return child_topic, created

def wiki_dfs(category_title, depth=0, stop_depth=0):
	#Create Topic object for this category_title
	topic, created = visit(category_title)

	#Evaluate stop condition  calling wiki_dfs('title') will default to one level deep search
	#Stop if we go too deep or hit a cycle
	if not created or depth > stop_depth:
		return topic

	#iterate through the adjacent nodes
	sub_list = scrapeCategoryPages(category_title)
	for child_title in sub_list:
		#Check if it is a category 
		split_title = child_title.split('Category:')
		is_category = len(split_title) == 2
		if len(split_title)>2:
			raise ValueError("%s split into more than two pieces" % category_title)

		#if page - create topic for page
		if not is_category:
			#Request page from api for each page
			child_topic, child_created = visit(child_title)

		#if category
		if is_category:
			#Recursively traverse child nodes
			child_topic = wiki_dfs(child_title, depth+1, stop_depth)

		#Add the new child_resource or topic to  topic.child_resources
		topic.child_resources.add(child_topic)
		topic.save()
	#Return the created topic after all children have been created, added and traversed
	return topic 


testCategory = 'Compiler_construction'
depth = 0
stop_depth = 3

wiki_dfs(testCategory, depth, stop_depth)