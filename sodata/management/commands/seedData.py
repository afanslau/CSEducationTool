from django.core.management.base import BaseCommand
from sodata.models import Resources, TopicRelations
from django.contrib.auth.models import User
from django.db.transaction import commit_on_success

# Get the system user
system_user, created = User.objects.get_or_create(username="System")
Resources.create_home(system_user)

class Command(BaseCommand):
	help = 'Load topic data from file'
	def handle(self, *args, **options):

		loadTopicFile('resources/seedData')

def loadTopicFile(filename):

	#Create the root
	root_title = 'Computer Science Topics'
	seed_root, root_created = Resources.objects.get_or_create(title=root_title)
	if root_created:
		seed_root.save()


	print(filename)
	with open(filename, 'r') as f:
		n_ve = [int(s.strip()) for s in f.readline().split()]
		n_V, n_E = n_ve
		print(n_ve)
		i = 0
		while i<n_V:
			v_title = f.readline().strip()
			print(v_title)
			t, created = Resources.objects.get_or_create(title=v_title, in_standard=True)
			if created: 
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
			pren, pre_created = Resources.objects.get_or_create(title=pres, in_standard=True) # Can I pass either a Topic object or a TopicID to the constructor?
			if pre_created:
				pren.save()
				print('insert into Topics %s  %s' % (pren.title, pren.id))
			postn, post_created = Resources.objects.get_or_create(title=posts, in_standard=True)  #use get_or_create to handle topics that were not previously added to the database
			if post_created:
				postn.save()
				print('insert into Topics %s  %s' % (postn.title, postn.id))
			
			#Create edge relationship
			rel, rel_created = TopicRelations.objects.get_or_create(from_resource=pren, to_resource=postn, perspective_user=system_user)
			print(rel.to_resource.title, rel.from_resource.title)
			i+=1
	


	# Attach all dangling references to the root
	topics = Resources.objects.filter(parent_resources=None, in_standard=True)
	for topic in topics:
		rel, rel_created = TopicRelations.objects.get_or_create(from_resource=seed_root, to_resource=topic, perspective_user=system_user)



	#Create many to many field references as well		
# 	for topic in Topics.objects.all():
# 		#Get all parent topics and add to parents ManyToManyField
# 		for child in TopicRelations.objects.filter(from_node=topic):
# 			topic.children.add(child.to_node)  #automatically sets the parent relationship?

# from sodata.models import Topics 
# ds = Topics.objects.get(title='Data Structures').children.all()
# for t in ds:
# 	print(t.title, t.children.all().values_list('title',flat=True))

# from sodata.models import Resources
# def out(t,a):
# 	return ['t.children: '+' '.join(t.parents.all().values_list('title',flat=True)), 't.parents: '+' '.join(t.parents.all().values_list('title',flat=True)), 'a.children: '+' '.join(a.parents.all().values_list('title',flat=True)), 'a.parents: '+' '.join(a.parents.all().values_list('title',flat=True))]

# toplevel_topics = Resources.objects.filter(from_relation=None)

# t = Resources.objects.get(title='Data Structures')
# a = Resources.objects.get(title='Arrays')
# out(t,a)
# a.parents.add(t)
# out(t,a)

