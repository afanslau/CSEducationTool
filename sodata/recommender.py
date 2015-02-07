from django.db.models import Q
from sodata.models import Resources, TopicRelations, UserRelation
import watson
from operator import itemgetter

w_watson_rank = 400
w_text_similarity = 400

w_total_relations = 55
w_child_role = 90
w_user_total_relations = 70

w_total_starred = 85
w_user_starred = 200

class RecContext(object):
	
	# What is the expected average and range for all of these values? 
	# They should probably be normalized and mean shifted before the weighting happens. 
	# How can I do that while minimizing the number of DB queries? 

	def __init__(self, user, resource=None, extra_terms=None):
		super(RecContext, self).__init__()
		self.resource = resource
		self.user = user
		self.extra_terms = extra_terms


	def get_relevance(self, candidate):

		try: 
			score = w_watson_rank * candidate.watson_rank
		except AttributeError:
			score = 0


		# Count the number of relations the candidate is a part of
		all_relations = TopicRelations.objects.filter(Q(from_resource=candidate)|Q(to_resource=candidate))
		score += w_total_relations * len(all_relations)

		# Count the number of relations where the candidate is a child of the context resource
		if self.resource is not None:
			child_role = all_relations.filter(from_resource=self.resource, to_resource=candidate)
			score += w_child_role * len(child_role)

		# Count the number of relations from the user's perspective
		user_created = all_relations.filter(perspective_user=self.user)
		score += w_user_total_relations * len(user_created)

		# Count the number of users who have starred the candidate
		all_starred = UserRelation.objects.filter(resource=candidate, starred=True)
		score += w_total_starred * len(all_starred)

		# Check if the context user has starred the candidate
		user_starred = all_starred.filter(user=self.user)
		if len(user_starred) > 1:
			# Log an error..
			print 'ERROR: UserRelation should be unique to a user-resource'
		score += w_user_starred if len(user_starred) > 0 else 0  # len(user_starred) should only be 0 or 1, UserRelation should be unique


		# TO-DO  Implement a text similarity score comparison between self.resource and candidate
		return score

	# TO-DO Implement this!
	def home_recommendations(self):

		# Recently active
		# Recently starred
		# Recently visited

		# Exclude all resources already pinned to your home page
		home_trs = TopicRelations.objects.filter(from_resource__author=self.user, from_resource__is_home=True)
		exclude_already_pinned_Q = ~Q(parent_resources__in=home_trs)

		# 
		# What happens when the user asks for more than 30 recommendations?
		urs = UserRelation.objects.all().order_by('-last_visited', '-starred')[:30]
		candidates = Resources.objects.filter(exclude_already_pinned_Q, user_relations__in=urs, is_home=False)

		with_rank = { c:self.get_relevance(c) for c in candidates }
		sorted_by_rank = sorted( with_rank.items() , key=itemgetter(1) , reverse=True)
		print 'recommender.home_recommendations  ', sorted_by_rank

		return [c[0] for c in sorted_by_rank]


	# TO-DO  Should I return a dictionary with the scores? probably should for testing purposes

	def recommend(self):
		base_qs = Resources.objects.filter(~Q(id=self.resource.id), is_home=False)


		if self.resource.is_home or self.resource is None:
			return self.home_recommendations()

		

		# Start by following all edges of the resource EXCEPT ones that I've already pinned
		trs = TopicRelations.objects.filter(~Q(perspective_user=self.user), from_resource=self.resource)

		related_Q = Q(parent_resources__in=trs)
		related_qs = base_qs.filter(related_Q)
		
		# Search the remaining resources with the resource title
		search_qs = watson.filter(Resources.objects.filter(~related_Q), self.resource.title)

		# Execute and concatenate queries, then sort
		candidates = list(related_qs) #+list(search_qs)

		with_rank = { c:self.get_relevance(c) for c in candidates }
		sorted_by_rank = sorted( with_rank.items() , key=itemgetter(1) , reverse=True)
		print 'recommender.recommend  ', sorted_by_rank

		return [c[0] for c in sorted_by_rank]


