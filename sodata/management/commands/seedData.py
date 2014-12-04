from django.core.management.base import BaseCommand
from sodata.models import Topics, TopicRelations
from django.db.transaction import commit_on_success

class Command(BaseCommand):
	help = 'Load topic data from file'
	def handle(self, *args, **options):
		i=0
		for a in args:
			loadTopicFile(a)
			i+=1
		print(i) 

# @staticmethod
def loadTopicFile(filename):
	#readLine to get edge
	print(filename)
	with open(filename, 'r') as f:
		n_ve = [int(s.strip()) for s in f.readline().split()]
		n_V, n_E = n_ve
		print(n_ve)
		i = 0
		while i<n_V:
			v_title = f.readline().strip()
			print(v_title)
			t, created = Topics.objects.get_or_create(title=v_title)
			if created: 
				t.save()
				print('insert into Topics %s  %s' % (v_title,t.id))
			else: print('already exists %s  %s' % (v_title,t.id))
			i+=1
		i=0
		while i<n_E:
			#Get the string
			preposts = [s.strip() for s in f.readline().split(',')]
			print(preposts)
			pres, posts = preposts

			#Get the object
			pren, pre_created = Topics.objects.get_or_create(title=pres) # Can I pass either a Topic object or a TopicID to the constructor?
			if pre_created:
				pren.save()
				print('insert into Topics %s  %s' % (pren.title, pren.id))
			postn, post_created = Topics.objects.get_or_create(title=posts)  #use get_or_create to handle topics that were not previously added to the database
			if post_created:
				postn.save()
				print('insert into Topics %s  %s' % (postn.title, postn.id))
			
			#Create edge relationship
			rel, rel_created = TopicRelations.objects.get_or_create(from_node=pren, to_node=postn)
			if rel_created: rel.save()
			print(rel.to_node.title, rel.from_node.title)
			i+=1
	
	#Create many to many field references as well		
# 	for topic in Topics.objects.all():
# 		#Get all parent topics and add to parents ManyToManyField
# 		for child in TopicRelations.objects.filter(from_node=topic):
# 			topic.children.add(child.to_node)  #automatically sets the parent relationship?

# from sodata.models import Topics 
# ds = Topics.objects.get(title='Data Structures').children.all()
# for t in ds:
# 	print(t.title, t.children.all().values_list('title',flat=True))

from sodata.models import Topics
def out(t,a):
	return ['t.children: '+' '.join(t.parents.all().values_list('title',flat=True)), 't.parents: '+' '.join(t.parents.all().values_list('title',flat=True)), 'a.children: '+' '.join(a.parents.all().values_list('title',flat=True)), 'a.parents: '+' '.join(a.parents.all().values_list('title',flat=True))]

toplevel_topics = Topics.objects.filter(from_relation=None)

t = Topics.objects.get(title='Data Structures')
a = Topics.objects.get(title='Arrays')
out(t,a)
a.parents.add(t)
out(t,a)

