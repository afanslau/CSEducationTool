from django.core.management.base import BaseCommand
from django.contrib.auth.models import AnonymousUser, User
from django.test import Client
from django.test import TestCase, RequestFactory

class Command(BaseCommand):
	help = 'lists all usernames'
	def handle(self, *args, **options):
		i = 0
		for u in User.objects.all().order_by('username'):
			print u.username
			i += 1
		print 'Total number of users is ', i