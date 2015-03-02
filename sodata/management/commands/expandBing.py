from django.core.management.base import BaseCommand
from sodata.models import Resources, TopicRelations
from django.contrib.auth.models import User 
import Bing 
from bs4 import BeautifulSoup as Soup

class Command(BaseCommand):
	help = 'Loads wikipedia topics from the api'
	def handle(self, *args, **options):

		bing_user,created = User.objects.get_or_create(username="Bing Search")
		if created:
			Resources.create_home(bing_user)
		system_user,created = User.objects.get_or_create(username="System")

		
		addons = ['introduction to','tutorial','example','getting started','learning','how to','essentials']
		tags_to_expand = ['Ruby on Rails','Git','Source Control','Software Engineering','Dependency Management']
		for tag in tags_to_expand:
			for addon in addons:

				tagr,created = Resources.objects.get_or_create(title=tag, author=system_user)
				res = Bing.perform_query(' '.join([addon, tag]), 3)
				soup = Soup(res)
				entries = soup.feed.find_all('entry')

				counted_errors = 0
				for entry in entries:
					# try:
					title = entry.content.find('d:title').get_text()
					url = entry.content.find('d:url').get_text()
					displayurl = entry.content.find('d:displayurl').get_text()
					text = entry.content.find('d:description').get_text()
					new, created = Resources.objects.get_or_create(title=title, text=text, url=url, display_url=displayurl, author=bing_user)
					TopicRelations.objects.get_or_create(to_resource=new, from_resource=tagr, perspective_user=bing_user)
					# except Exception:
					# 	counted_errors += 1
					print 'Created resource ', created, new.id, new.title 
