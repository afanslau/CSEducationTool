from django.core.management.base import BaseCommand
from sodata import learning
class Command(BaseCommand):
	help = 'Loads wikipedia topics from the api'
	def handle(self, *args, **options):
		learning.get_tfidfvectorizer(train=True)