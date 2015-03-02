from django.db.models import Q
from sodata.models import Resources, TopicRelations, UserRelation
from sodata import learning
from sklearn.preprocessing import normalize


# Numpy is not supported by default on Heroku  
# heroku config:set BUILDPACK_URL=https://github.com/thenovices/heroku-buildpack-scipy.git
# Source: https://blog.dbrgn.ch/2013/6/18/heroku-buildpack-numpy-scipy-scikit-learn/
# Source2:  http://stackoverflow.com/questions/11635857/how-to-install-scikit-learn-on-heroku-cedar
# https://github.com/alyssaq/heroku-buildpack-python-sklearn
import numpy as np
import watson
from operator import itemgetter

from django.db.models import Sum

from sodata import constants


def normalize_weights(weights):
	total = sum(weights.values())
	if total==0:
		return weights
	return {feature : w/total for feature,w in weights.items()}
weights = normalize_weights({
	'watson_rank'     					: 20,
	'text_similarity' 					: 70,
	'total_views'     					: 10,
	'relations_context_to_candidate'    : 40,
	'human_created'    					: 40,
	# 'recently_used'   					: 40
})



class RecCandidate(object):
	def __init__(self, context, resource, path=None):
		super(RecCandidate, self).__init__()
		self.resource = resource
		# Store the path it took to get from the context to here
		self.path = path if path is not None else []
		self.context = context
	def __eq__(self, other):
		return self.resource == other.resource
	def __hash__(self):
		return hash(self.resource)


class RecContext(object):
	
	# What is the expected average and range for all of these values? 
	# They should probably be normalized and mean shifted before the weighting happens. 
	# How can I do that while minimizing the number of DB queries? 

	def __init__(self, user, resource=None, candidates=None, important_terms=None):
		super(RecContext, self).__init__()
		
		self.resource = resource
		self.user = user		
		
		self.important_terms = set(important_terms) if important_terms is not None else set()
		self._add_important_terms()


		self.candidates = set()
		self.candidate_ids = set()
		self.add_candidates(candidates)


	def add_candidates(self, candidates):
		if candidates is None:
			return
		self.candidates = self.candidates.union(candidates)
		self.candidate_ids = self.candidate_ids.union([c.resource.id for c in candidates])

	def get_relevance(self, candidate):

		resource = candidate.resource

		try: 
			score = weights['watson_rank'] * resource.watson_rank  # Should weight by the importance of the term that it was matched to
		except AttributeError:
			score = 0

		# Get the textual similarity
		similarity = learning.get_similarity(self.resource,resource)[0,1]
		score += weights['text_similarity'] * similarity

		# Get the number of views by all users
		n_views = UserRelation.objects.filter(resource=resource).aggregate(Sum('num_visits'))['num_visits__sum']
		score += weights['total_views'] * (1 - 1/n_views) if n_views > 0 else 0
		# TODO squash between 0 and 1

		# If the resource was created by a human, weight higher
		if resource.author is not None:
			score += weights['human_created'] * int(resource.author.is_human())

		# Count the number of relations where the candidate is a child of the context resource
		if self.resource is not None:
			child_role = TopicRelations.objects.filter(from_resource=self.resource, to_resource=resource)
			score += weights['num_relations_context_to_candidate'] * (1 - 1/len(child_role)) if len(child_role) > 0 else 0

		
		# # Get the cost-weighted path length from query
		# path_sum = 0
		# for i in range(len(candidate.path)):
		# 	parent = candidate.path[i]
		# 	try:
		# 		child = candidate.path[i+1]
		# 	except IndexError:
		# 		child = candidate.resource

		# 	# Find TopicRelations between those two resources

		# 	print 'get_relevance  ', parent.id, parent.title, child.id, child.title


		# 	path_relations = TopicRelations.objects.filter(from_resource=parent, to_resource=child)

		# 	# Multiply by the average confidence. Since confidence is always between 0 and 1, the path_sum will become smaller as the distance gets larger
		# 	# Scale down the confidence unless th

		# 	if len(path_relations) == 0:
		# 		print 'child is not related to parent! WHY'
		# 		path_sum = 0
		# 	else: # Fail Gracefully
		# 		path_sum *= sum([tr.confidence * ((1 - USER_WEIGHT) if tr.perspective_user != self.user else 1) for tr in path_relations]) / len(path_relations)
		# score += w_path_confidence * path_sum

		# # Count the number of relations the candidate is a part of
		# all_relations = TopicRelations.objects.filter(Q(from_resource=resource)|Q(to_resource=resource))

		# # TODO - find a better way to bound between 0 and 1
		# score += w_total_relations * (1 - 1/len(all_relations))


		# Count the number of relations from the user's perspective
		# user_created = all_relations.filter(perspective_user=self.user)
		# score += w_user_total_relations * len(user_created)

		# Count the number of users who have starred the candidate
		# all_starred = UserRelation.objects.filter(resource=candidate, starred=True)
		# score += w_total_starred * len(all_starred)

		# Check if the context user has starred the candidate
		# user_starred = all_starred.filter(user=self.user)
		# if len(user_starred) > 1:
		# 	# Log an error..
		# 	print 'ERROR: UserRelation should be unique to a user-resource'
		# score += w_user_starred if len(user_starred) > 0 else 0  # len(user_starred) should only be 0 or 1, UserRelation should be unique


		# TO-DO  Implement a text similarity score comparison between self.resource and candidate
		return score



	# TO-DO  Should I return a dictionary with the scores? probably should for testing purposes
	def follow_edges_with_path_length(self, resource, path_length=1, path=None, extra_Q=None):


		# Generate _path if needed
		new_path = list(path) if path is not None else [] # list() creates a copy of the list, passing it by value

		# Make _candidate a RecCandidate if it isn't already one
		parent_candidate = resource if type(resource) is RecCandidate else RecCandidate(context=self, resource=resource, path=new_path)

		# print 'follow_edges_with_path_length: resource: ',parent_candidate.resource.id,parent_candidate.resource.title
		# print '   path: ', new_path 

		# After I follow all the edges, add the node to the path. 
		exclude_Q = ~Q(id__in=self.candidate_ids)
		if extra_Q is not None:
			exclude_Q = exclude_Q&extra_Q

		new_candidates = self.follow_edges(parent_candidate, exclude_Q)  # Follow all relations to resources that match the Q
		self.add_candidates(new_candidates)

		# Then check the base case
		if len(new_path) == path_length:
			return
		else:
			for c in new_candidates:
				self.follow_edges_with_path_length(c, path_length, new_path, extra_Q)


	def follow_edges(self, resource, extra_Q=None, relation_Q=None): 

		# Extract the _path and parent _resource
		if type(resource) is RecCandidate:
			_resource = resource.resource  
			_path = list(resource.path)
		else: 
			_resource = resource 
			_path = []
		_path += [_resource]
		
		# print 'call follow_edges: ', _resource.id, _resource.title, '\n   _path ', _path

		# Get children of _resource
		_relation_Q = Q(from_resource=_resource)|Q(to_resource=_resource) 
		if relation_Q is not None:
			_relation_Q = _relation_Q & relation_Q
		trs = TopicRelations.objects.filter(_relation_Q)
		_resource_Q = Q(parent_resources__in=trs) | Q(child_resources__in=trs)
		if extra_Q is not None:
			_resource_Q = _resource_Q & extra_Q
		res = Resources.objects.filter(_resource_Q, is_home=False)

		# Create candidates from children, add path
		return [ RecCandidate(context=self, resource=r, path=_path) for r in res ]
		

	def fill_candidates(self):

		# Fill candidates by traversing the graph n levels deep

		# First, follow the edges of the children on screen 
		pinned_trs = TopicRelations.objects.filter(perspective_user=self.user, from_resource=self.resource)
		pinned_Q = Q(parent_resources__in=pinned_trs)
		# pinned = list(Resources.objects.filter(pinned_Q, is_home=False)) # Evaluate immediately so that nothing changes when i change the Q

		# print 'method: fill_candidates  pinned: ', len([(c.id, c.title) for c in pinned])

		# # Exclude the following from the candidate list

		# When I re-introduce the graph traversal, need to change this back to ~
		exclude_Q = pinned_Q|Q(id=self.resource.id)|Q(is_home=True)
		
		# _path = [self.resource]
		# for r in pinned:
		# 	self.follow_edges_with_path_length(resource=r, path_length=SEARCH_PATH_LENGTH, path=_path, extra_Q=exclude_Q)

		# # Then follow other edges of self.resource (those pinned by other users)
		# self.follow_edges_with_path_length(resource=self.resource, path_length=SEARCH_PATH_LENGTH, extra_Q=exclude_Q)


		

		# Add other candidates by FTS and most viewed
		# Get the most important keywords in the context

		# Search Watson for vocab_terms

		# print 'method: fill_candidates  self.important_terms: ', self.important_terms

		for term in self.important_terms:
			search_results = watson.search(term, exclude=(Resources.objects.filter(exclude_Q),))[:constants.N_RECOMMENDATIONS_PER_TERM]
			self.add_candidates([RecCandidate(resource=sr.object, context=self) for sr in search_results]) 






		# # Get the most viewed topics (#TODO in the last t time)
		# most_viewed_resources = Resources.objects.filter(is_home=False).annotate(total_views=Sum('user_relations__num_visits')).order_by('-total_views')[:NUM_MOST_VIEWED_CANDIDATES]
		# self.add_candidates([RecCandidate(resource=r, context=self) for r in most_viewed_resources])


	def rank_candidates(self):

		with_rank = { c:self.get_relevance(c) for c in self.candidates }
		sorted_by_rank = sorted( with_rank.items() , key=itemgetter(1) , reverse=True)
		# print 'recommender.recommend  ', len(sorted_by_rank)

		return [c[0].resource for c in sorted_by_rank]


		# TODO FILL THIS IN

	def recommend(self):
		self.fill_candidates()

		print 'recommend  important_terms: ', self.important_terms

		return self.rank_candidates()
		# return []
		

	def _add_important_terms(self):
		tfv = learning.get_tfidfvectorizer()
		docs = []
		if not self.resource.is_home:
			# Use the title and text from the parent at a higher weight
			doc = self.resource.get_doc_string()
			if doc != '':
				docs += [doc] * constants.TITLE_WEIGHT  # Weight the parent_resource more than the children

		# Read texts of children 
		trs = TopicRelations.objects.filter(perspective_user=self.user, from_resource=self.resource)
		if len(trs) > 0:
			docs += [r.get_doc_string() for r in Resources.objects.filter(parent_resources__in=trs, is_home=False)]


		# print '_add_important_terms  docs: ', docs

		# Add default interests
		if len(docs) > 0:
			
			transformed = tfv.transform(docs)

			# print '_add_important_terms  tfv: ', tfv

			vect = np.array(transformed.sum(axis=0)).flatten()  # Doesnt need to be normalized, because I'm just sorting it to get vocab
			# Since I'm only getting the top N, it's unneccessary to sort the rest of the list
			vix = learning.argtopk(vect, k=constants.N_IMPORTANT_TERMS)
			vix = vix[vect[vix].nonzero()]  # Eliminate the zero entries
			word_list = [learning.index_vocab_map[ix] for ix in vix]

			print '_add_important_terms  ', word_list

			self.important_terms = self.important_terms.union(word_list)

		if len(self.important_terms) == 0:
			self.important_terms = self.important_terms.union(['ruby','rails','git','source control','software engineering','rvm','blog','dependency'])

		print '_add_important_terms  ', self.important_terms

