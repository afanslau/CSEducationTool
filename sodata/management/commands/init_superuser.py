from django.core.management.base import BaseCommand
from sodata.models import Resources
from django.contrib.auth.models import User
class Command(BaseCommand):
	help = 'Loads wikipedia topics from the api'
	def handle(self, *args, **options):
		for u in User.objects.all():
			Resources.create_home(u)
