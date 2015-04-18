from django.core.management.base import BaseCommand
from sodata.models import Resources, TopicRelations, get_system_user, get_bing_user
from django.contrib.auth.models import User 
import Bing 
from bs4 import BeautifulSoup as Soup

import random

class Command(BaseCommand):
	help = 'Loads wikipedia topics from the api'
	def handle(self, *args, **options):

		bing_user = get_bing_user()
		system_user = get_system_user()
		# bing_user,created = User.objects.get_or_create(username=SYSTEM_USERNAME)
		# if created:
			# Resources.create_home(bing_user)
		# system_user,created = User.objects.get_or_create(username="System")


		
		addons = ['']
		tags_to_expand = ['web development','html','css','javascript','django','introduction to web development']
		#['objects vs. classes java explained','java method signature','java new keyword explanation']
		# tags_to_expand = ['pieces of a java program','java hangman tutorial','java class walkthrough', 'learning java','java topics', 'java beginner', 'object oriented programming','objects vs. classes java explained','java method signature','java new keyword explanation']
		for tag in tags_to_expand:
			for addon in addons:


				tagr,created = Resources.objects.get_or_create(title=tag, author=system_user)
				
				results = Bing.get_resources_for_query(' '.join([addon, tag]), top=30)

				for new in results[:5]:
				# soup = Soup(res)
				# entries = soup.feed.find_all('entry')

				# counted_errors = 0
				# for entry in entries:
				# 	# try:
				# 	url = entry.content.find('d:url').get_text()
				# 	new, created = Resources.objects.get_or_create(url=url)
				# 	if created:
				# 		new.title = entry.content.find('d:title').get_text()	
				# 		new.displayurl = entry.content.find('d:displayurl').get_text()
				# 		new.text = entry.content.find('d:description').get_text()
				# 		new.author = bing_user

					TopicRelations.objects.get_or_create(to_resource=new, from_resource=tagr, perspective_user=bing_user)
					# except Exception:
					# 	counted_errors += 1
					print 'Created resource ', new.id, new.title 
