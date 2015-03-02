from django.core.management.base import BaseCommand
from django.contrib.auth.models import AnonymousUser, User
from django.test import Client
from django.test import TestCase, RequestFactory

class Command(BaseCommand):
	help = 'Creates users with randomized usernames and default passwords'
	def handle(self, *args, **options):
		try:
			n = int(args[0])
		except IndexError:
			n = 10

		self.user = AnonymousUser()
		c = Client()
		# self.request_factory = RequestFactory()
		self.username_factory = UsernameFactory()
		for i in range(n):
			username = self.username_factory.get_random_username()
			response = c.post('/api/register',{'username':username, 'password':'password'})
			print 'created user : ', i, response
			# register_request = self.factory.post('/api/register')
			# request.user = self.user
			# response = api_register



class UsernameFactory(object):
	"""Generates random usernames"""
	def __init__(self, *args):
		super(UsernameFactory, self).__init__()
		self.adjs = set(['imperialist','defiant','sleepiest','tan','jumbo','tiny','blue','unarmed','manic','entranced'])
		self.nouns = set(['tripod','headphone','distraction','spectacle','contamination','ocean','skyscraper','greenhouse','mammal','cove'])
		self.usernames = set()
		for a in self.adjs:
			for n in self.nouns:
				self.usernames.add(a+'-'+n)
	
	def get_random_username(self):
		try:
			return self.usernames.pop()
			# w1 = self.adjs.pop()
			# w2 = self.nouns.pop()
			# words = [w1,w2]
			# validated_words = []
			# for i,w in enumerate(words):
			# 	to_check = w
			# 	while to_check in self.used_words:
			# 		if i == 0:
			# 			to_check = self.adjs.pop()
			# 		else:
			# 			to_check = self.nouns.pop()
			# 	validated_words.append(to_check)
			# 	self.used_words.add(to_check)
			# return '-'.join(validated_words)
		except KeyError:
			return None
