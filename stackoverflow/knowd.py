from django.db.models import Q

import datetime

from scripts import loadTermMatrix as so 
from stackoverflow.models import SOUsers, SOPosts

import numpy as np 
from scipy.sparse import csr_matrix
from scipy import stats
import matplotlib.pyplot as plt
import pickle
import random

from sklearn.preprocessing import scale, normalize 
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics import average_precision_score

from operator import attrgetter
import copy


# n_users=20
# n_samples_per_user=100
# n_terms=20
# n_gram = 3

# For weekly_term prediction method

class KnowdGraph():	

	def __init__(self, n_terms=500, n_gram=3, n_recent_docs=5, n_recent_terms=5, params=None):
		
		# Parameters
		self.n_terms = n_terms
		self.n_gram = n_gram
		self.n_recent_docs = n_recent_docs
		self.n_recent_terms = n_recent_terms
		self.params = params if params else {
			'wtd_doc':0.4, 
			'wtd_tag':0.6
		}

		# Params get set on data initialization
		self.n_samples_per_user = None
		self.so_users = None 
		self.n_users = None 
		

		# Fields
		self.tfidf_vectorizer = None

		# Data Structures
		self.term_index_map = {} # term --> term_index
		

		# Database references
		self.doc_index_map = {}  # post.id --> doc_index
		self.user_index_map = {} # user.id --> user_index
		

		# Data
		self.docs = [] # Docs
		self.terms = np.array([])
		self.tag_docs = [] # Tag lists - for stackoverflow, assumed to be tags created by the author
		self.user_doc_indices = {} # user_index --> set of associated documents
		self.vocab = set() # Terms


		# csr_matrices
		self.wtd = None
		self.wtt = None
		self.wtu = None 


	def init_data_from_so(self, q_post=None, so_users=None, so_posts=None, n_users=None, n_samples_per_user=100, random_post_choice=True):
		self.n_samples_per_user = n_samples_per_user
		# Set variables
		_post_Q=~Q(tags=None)
		if q_post:			
			post_Q = _post_Q & q_post
		else:
			post_Q = _post_Q

		if not n_users and not so_users:
			n_users = 20 # Default n_users
		# Fetch users
		if so_users:
			if not n_users:
				n_users = len(so_users)
			self.so_users = so_users[:n_users]
		else:
			self.so_users = SOUsers.objects.all().order_by('-reputation')[:n_users] #.annotate(num_posts=Count('owned_posts'))
		self.n_users = len(self.so_users) #len(self.so_users)

		# Fetch posts for each user
		for ui,u in enumerate(self.so_users):
			# Get posts for this user
			print 'Get posts for user ', ui, u.id

			if so_posts and u.id in so_posts:
				_u_posts = so_posts[u.id]
			else:
				_u_posts = SOPosts.objects.filter(post_Q, owner_user=u).order_by('-creation_date')  #.order_by('-score')

			u_posts = list(_u_posts)
			if random_post_choice:
				random.shuffle(u_posts)
			u_posts = u_posts[:n_samples_per_user]
			# Store documents in memory
			u_docs, post_index_map = so.vectorize_so_posts(u_posts)
			self.user_doc_indices[ui] = set() # To be filled in with doc indices
			for p in u_posts:
				doc_index = post_index_map[p.id]
				d = u_docs[doc_index]
				tagdoc = ' '.join(p.tags.strip('><').split('><')) if p.tags is not None else ''
				self.docs.append(d)
				self.tag_docs.append(tagdoc)

				# Database mapping
				di = len(self.docs) - 1
				self.doc_index_map[p.id] = di
				self.user_index_map[u.id] = ui
				self.user_doc_indices[ui].add(di)

	def init_data_with_sub_graph(self, kg, n_samples_per_user=50):

		self.n_samples_per_user = n_samples_per_user
		self.so_users = kg.so_users

		for ui,u in enumerate(self.so_users):
			doc_indices = kg.user_doc_indices[ui]

		

	# def get_subgraph(self, n_samples_per_user=50):
	# 	if self.n_samples_per_user <= n_samples_per_user:
	# 		raise ValueError("Sub-graph size must be smaller than the entire graph. Use a smaller value for parameter `n_samples_per_user`") # Should be a deep copy

	# 	# Create a new KnowdGraph
	# 	# For each user, get a sub-set of the documents
	# 	kg = KnowdGraph()



		# Get all posts authored by any of those users
		# sample_posts = SOPosts.objects.filter(owner_user__in=self.users)
		# print '__init__ sample_posts:  ', len(sample_posts)

	def train_with_so(self, q_post=None, so_users=None, so_posts=None, n_users=20, n_samples_per_user=100, vocab=None, random_post_choice=True):
		self.init_data_from_so(q_post=q_post,so_users=so_users,so_posts=so_posts,n_users=n_users,n_samples_per_user=n_samples_per_user,random_post_choice=random_post_choice)

		# Process data
		if vocab:
			self.vocab = vocab
		self.learn_weights()
		return self

	def train_with_example(self):
		terms = ['web','django','html','databases','algorithms']
		# terms = ['web','front','back','html','css',
		# 		 'js','django','python','ruby','mvc',
		# 		 'algorithms','tcp','recursion','unix',
		# 		 'graphics','cpu','server']
		term_index_map = {k:i for i,k in enumerate(terms)}

		n_terms = len(terms)
		n_users = 3
		n_docs = 5

		# tf = np.array([
		# 	[4,3,5,2,1,1,0,0,1,0,0,0,0,0,0,0,0],		# Overview doc
		# 	[0,0,0,10,6,11,1,1,0,0,0,0,0,0,0,1],		# Back & Front
		# 	[0,2,0,9,4,7,0,0,0,0,0,0,0,0,0,0,0],		# mostly front
		# 	[0,0,0,1,0,5,1,1,4,2,0,0,0,0,0,0,1],		# mostly back
		# 	[0,0,0,0,0,0,5,5,5,5,0,0,0,0,0,1,3],		# all back
		# 	])
		tf = np.array([
			[5,4,5,1,0],		# Web overview
			[3,2,2,0,0],		# Web overview
			[4,1,10,1,0],		# HTML
			[1,1,7,1,1],		# HTML
			[1,9,1,8,1],		# Backend
			[2,7,0,10,0],		# Databases
			])
		self.tf = tf
		# Generate docs from contrived example
		docs = []
		for di,dv in enumerate(tf):
			wordlist = []
			for ti,freq in enumerate(dv):
				wordlist.extend([terms[ti]]*freq)
			docs.append(' '.join(wordlist))



		user_doc_indices = {
			0:[0,2,3], 	# Overview user
			1:[1,4,5],  # Alice
			# 2:[4,5]	# Back, learning some front
		}


		return self.train_with_data(docs=docs, vocab=terms, user_doc_indices=user_doc_indices, use_tags=False)




	def train_with_data(self, docs=None, vocab=None, tag_docs=None, user_doc_indices=None, n_terms=None, use_tags=True):

		# Initialize Data
		if docs:
			self.docs = docs
		if tag_docs:
			self.tag_docs = tag_docs
		if vocab:
			self.vocab = vocab
		if user_doc_indices:
			self.user_doc_indices = user_doc_indices
			self.n_users = len(self.user_doc_indices)
		if n_terms:
			self.n_terms = n_terms
		else:
			self.n_terms = len(self.vocab)

		# Train
		self.learn_weights(use_tags=use_tags)
		return self

	def re_train_vocab(self, n_terms=20):
		self.vocab = set()
		self.learn_weights()

	def learn_weights(self, use_tags=True):
		

		# Learn Vocab
		if len(self.vocab)==0:
			# learn vocab from tags
			self.tag_count_vectorizer = CountVectorizer(stop_words='english', max_features=self.n_terms, binary=True)
			self.tag_matrix = self.tag_count_vectorizer.fit_transform(self.tag_docs)
			self.vocab = set(self.tag_count_vectorizer.vocabulary_.keys())

			# learn vocab from docs
			doc_vectorizer = TfidfVectorizer(stop_words='english', max_features=self.n_terms) # use min_df and max_df
			doc_vectorizer.fit(self.docs)

			# combine to get final vocab
			learned_terms = set(doc_vectorizer.vocabulary_.keys())
			if type(self.vocab) is list:
				new_terms = (set(self.vocab) ^ learned_terms) & learned_terms
				self.vocab.extend(list(new_terms))
			elif type(self.vocab) is set:
				self.vocab = self.vocab.union(learned_terms)
		self.n_terms = len(self.vocab) # this is wrong. need to limit to n_terms. n_terms should be immutable 

		
		# Fit & Transform with self.vocab
		self.tfidf_vectorizer = TfidfVectorizer(vocabulary=self.vocab, norm='l2')
		self.doc_matrix = self.tfidf_vectorizer.fit_transform(self.docs)
	
		self.term_index_map = self.tfidf_vectorizer.vocabulary_
		invterm = {v:k for k,v in self.term_index_map.items()}
		self.terms = np.array([invterm[i] for i in range(len(invterm))])



		# Calculate weights


		''' WTD Equation '''
		
		if use_tags:
			self.tag_matrix = self.tfidf_vectorizer.fit_transform(self.tag_docs)  # Does it make sense to fit to both?
			self.wtd = self.params['wtd_doc'] * self.doc_matrix + self.params['wtd_tag'] * self.tag_matrix
		else:
			self.wtd = self.params['wtd_doc'] * self.doc_matrix
		
		''' WTD Equation '''


		''' WTT Equation '''
		# init Wtt as similarity matrix
		# search google for how to do this correctly
		self.wtt = (self.wtd.T * self.wtd) # multiply by transpose
		# Does this normalize by vector size? I don't think so
		''' WTT Equation '''


		''' WTU Equation '''
		# # There is definitely a more efficient linear algebra way to do this
		# # initialize a csr_matrix
		densewtu = np.zeros((self.n_users,self.n_terms))
		for u in range(self.n_users):
			densewtu[u,:] = self.get_user_vector(u)
		self.wtu = csr_matrix(densewtu)

		''' WTU Equation '''

	def get_user_vector(self, user):
		# mydocs = SOPosts.objects.filter(owner_user=user)  #improve  Select only id field
		# mydocs = [self.docs[di] for di in self.user_doc_indices[user.id]]
		# Get wtd matrix indices from the doc_index_map
		doc_indices = np.array([i for i in self.user_doc_indices[user]])
		# Get the wtd matrix of only documents that user interacted with		

		# User has no documents that match the query. wtd = zeros
		if len(doc_indices) == 0:
			return np.zeros((1, self.n_terms))

		user_wtd = self.wtd[doc_indices,:]
		# Take the average wtd across topics (columns)
		wu = np.array(user_wtd.mean(0)).flatten() #mean returns a 1 X n_terms matrix. Convert to array and flatten to vector
		return wu


	def sort_users_by_interest_in_term(self, term):
		return np.argsort(self.wtu[:,self.term_index_map[term]].todense())[:,::-1]

	def sort_terms_by_interest_for_user(self, users=None):
		# Fix to allow argsorting with 2d matrix
		return np.argsort(self.wtu[users,:].todense())[:,::-1]



	def predict(self, context_term, user, baseline=False):
		# Sort all topics by relevance
		context_i = context_term if type(context_term) is not str else self.term_index_map[context_term]
		ui = user if type(user) is int else self.user_index_map[user.id]
		user_param = [1]*self.n_terms if baseline else [self.wtu[ui,ti] + .001 for ti in range(self.n_terms)]
		return np.array([self.wtt[ti,context_i] * user_param[ti]  for ti in range(self.n_terms)])

	def predict_all(self, context_term=None, baseline=False, random_predict=False):

		if random_predict:
			return np.random.random((self.n_users, self.n_terms))

		# For each user 
		topic_prediction = np.zeros((self.n_users, self.n_terms))
		# ranked_prediction = {}

		for ui in range(self.n_users):


			if context_term:
				term = context_term
			else:
				# Get what their favorite topic has been recently

				# Use only the most recent documents to get the recent_wtu
				# Sort by doc index and take the top n  -  docs are already sorted by (-user.reputation, -post.creation_date)    
				recent_docs_i = np.array(sorted(self.user_doc_indices[ui])[:self.n_recent_docs])
				if recent_docs_i.size > 0:
					recent_wtd = self.wtd[recent_docs_i,:]

					# Get the most important topics. Take the mean along axis 0 and argsort
					recent_wtu = np.array(recent_wtd.mean(0)).flatten()
				else:
					recent_wtu = np.zeros(self.n_terms)
				term = np.argsort(recent_wtu)[::-1][0] #  [:self.n_recent_terms]


			predicted_terms = self.predict(context_term=term, user=ui, baseline=baseline)

			print 'user: ', ui, 'predicted_terms: ', [self.terms[ti] for ti in np.argsort(predicted_terms)[::-1][:5]]

			topic_prediction[ui,:] = predicted_terms



		return topic_prediction



	def compare_to_test(self, kg_test, baseline=False, random_predict=False):
		y_true = np.array(kg_test.wtu.todense())
		nz = y_true.nonzero()
		nz_mean = y_true[nz[0], nz[1]].mean()
		nz_std = y_true[nz[0], nz[1]].std()
		thrsh = nz_mean + nz_std


		y_true =  (y_true > thrsh) *1.  # Convert from Boolean to Float
		y_score = self.predict_all(baseline=baseline, random_predict=random_predict)



		# print 'compare_to_test  y_true: ', y_true.shape, self.n_users, kg_test.n_users
		# print 'compare_to_test scores: ', [(y_true[u,:].dtype,y_score[u,:].dtype) for u in range(self.n_users)]
		# print 'compare_to_test  y_score: ', np.nonzero(~np.isfinite(y_score))

		# mean_avg = np.array([average_precision_score(y_true[u,:],y_score[u,:]) for u in range(self.n_users)])
		all_ap = np.zeros(self.n_users)
		for u in range(self.n_users):
			yt = y_true[u,:]
			ys = y_score[u,:]

			if yt.any() and ys.any():
				ap = average_precision_score(yt, ys)
			else:
				ap = 0
				print "WARNING in compare_to_test:  y_true and y_score must not be all zeros. Each sample user must have authored documents."

			all_ap[u] = ap
			
		return all_ap

		# Recommend in context of that topic

		# Check against test set to see if we were "right"


	# @classmethod
	# def train_test_with_so(cls, q_train=None, q_test=None, n_terms=500, n_users=100):
	# 	if q_train is None:
	# 		q_train = Q(creation_date__lt=datetime.datetime(2010,2,1))
	# 	if q_test is None:
	# 		q_train = Q(creation_date__lt=datetime.datetime(2010,4,1))		


	# 	# Train two graphs with different data sets
	# 	kg_train = KnowdGraph(n_terms=n_terms)
	# 	kg_train.train_with_so(q_post=q_train, n_users=n_users)
	# 	kg_test = KnowdGraph()
	# 	kg_test.train_with_so(q_post=q_test, n_users=n_users,vocab=kg_train.vocab)
	# 	return kg_train, kg_test





def dates_hist(posts):
	dates = [date_to_epoch(datetime.datetime.combine(p.creation_date, datetime.datetime.min.time())) for p in posts]
	bins = range(int(min(dates)),int(max(dates)),int(datetime.timedelta(weeks=5).total_seconds()))
	labels = [epoch_to_date(d).strftime('%m/%d/%y') for d in bins]
	plt.title('Distribution of number of posts by date')
	plt.xticks(bins,labels)
	plt.hist(dates)
	plt.show()
def epoch_to_date(e):
	return datetime.timedelta(seconds=e) + datetime.datetime(1970,1,1)
def date_to_epoch(d):
	return (d - datetime.datetime(1970,1,1)).total_seconds()



def pickle_post_ids(filename, users, n_samples_per_user=None, post_q=None):
	if not post_q:
		post_q = Q()
	cached_posts = {}
	for ui,u in enumerate(users):
		u_cached_posts = list(SOPosts.objects.filter(post_q, owner_user=u).order_by('-creation_date')[:n_samples_per_user])[::-1]		
		if len(u_cached_posts) > 20:
			cached_posts[u.id] = [p.id for p in u_cached_posts]
			print 'Fetching posts for user ', ui, u.id
			print '     num_posts for user ', u, ' : ', len(u_cached_posts), len(cached_posts)
	with open(filename,'w') as f:
		pickle.dump(cached_posts, f)
	return cached_posts


def bmatrix(a):
    """Returns a LaTeX bmatrix

    :a: numpy array
    :returns: LaTeX bmatrix as a string
    """
    if len(a.shape) > 2:
        raise ValueError('bmatrix can at most display two dimensions')
    lines = str(a).replace('[', '').replace(']', '').splitlines()
    rv = [r'\begin{bmatrix}']
    rv += ['  ' + ' & '.join(l.split()) + r'\\' for l in lines]
    rv +=  [r'\end{bmatrix}']
    return '\n'.join(rv)


# def run():
# 	'training...'
# 	kg_train, kg_test = KnowdGraph.train_test_with_so(n_terms=50, n_users=10)
# 	'testing...'
# 	precision = kg_train.compare_to_test(kg_test)
# 	print 'Precision: ', precision
# 	return kg_train, kg_test, precision

if __name__ == '__main__':
	try: 
	# This is supposedly bad practice (to test for the existince of a variable), but for a script I don't see a disadvantage yet 
	# http://stackoverflow.com/questions/843277/how-do-i-check-if-a-variable-exists-in-python
		if run_now:
			print 'loading cache file  \'',pickle_filename,'\'...'	
			n_users = None
			n_train_samples = 10
			n_test_samples = None
			# so_users = None

			with open(pickle_filename,'r') as f:
				user_doc_indices = pickle.load(f)

			print 'fetching ',len(user_doc_indices),' users from database...'
			all_user_ids = user_doc_indices.keys()
			# random.shuffle(all_user_ids)
			all_user_ids = all_user_ids[:n_users]
			all_users = SOUsers.objects.filter(id__in=all_user_ids)
			n_users = len(all_user_ids)


			# all_post_ids = sum([user_doc_indices[uid] for uid in all_user_ids],[])
			# print 'fetching ', len(all_post_ids), 'posts from database...'
			# all_posts = SOPosts.objects.filter(id__in=all_post_ids)
			all_posts = {}
			for ui,u in enumerate(all_users):
				print 'fetching posts for user: ',ui,u.id
				all_posts[u.id] = list(SOPosts.objects.filter(id__in=user_doc_indices[u.id]))



			# so_posts = {}
			# for p in all_posts:
			# 	this_doc = [p]
			# 	try:
			# 		existing_docs = so_posts[p.owner_user.id]
			# 		existing_docs.extend(this_doc)
			# 	except KeyError:
			# 		so_posts[p.owner_user.id] = this_doc
			# so_users = SOUsers.objects.filter(id__in=)[:n_users]
			# n_users = len(so_users)				

			print 'training with ',n_users,' users...'
			kg_train = KnowdGraph(n_terms=50)
			kg_train.train_with_so(n_users=n_users, so_users=all_users, so_posts=all_posts, n_samples_per_user=n_train_samples, random_post_choice=False)

			kg_test = KnowdGraph()
			kg_test.train_with_so(n_users=n_users, so_users=all_users, so_posts=all_posts, n_samples_per_user=n_test_samples, vocab=kg_train.vocab, random_post_choice=False)

			print 'testing...'
			precision = kg_train.compare_to_test(kg_test)
			baseline_precision = kg_train.compare_to_test(kg_test, baseline=True)
			random_precision = kg_train.compare_to_test(kg_test, random_predict=True)
			mean_precision = precision.mean()
			mean_baseline_precision = baseline_precision.mean()
			mean_random_precision = random_precision.mean()
			print 'Precision: ', mean_precision, precision
			print 'Baseline Precision: ', mean_baseline_precision, baseline_precision
			print 'Random Precision: ', mean_random_precision, random_precision
			print 'Percent Difference %2.5f %%' % ((mean_precision - mean_baseline_precision) / mean_baseline_precision * 100)

			# Paired Samples T-Test
			baseline_t_statistic, baseline_p_value = stats.ttest_rel(precision, baseline_precision)
			random_t_statistic, random_p_value = stats.ttest_rel(precision, random_precision)
			print 'Paired Samples T-Test  -  ', 'Baseline: ', (baseline_t_statistic, baseline_p_value), 'Random: ', (random_t_statistic, random_p_value)

			# Boxplot
			bpd = plt.boxplot([precision, baseline_precision, random_precision], labels=['Topic Similarity and User Preferences','Topic Similarity Only','Random Predictions'], showmeans=True)
			plt.ylabel('Average Precision', size=20)
			plt.title('Recommendation Precision for Users with the Over 20 Posts', size=20)
			# plt.title('Recommendation Precision for Users with the Most Authored Posts')
			# plt.title('Recommendation Precision for Users with the Highest Reputation')
			# plt.title("Recommendation Precision for Users with Posts Tagged as 'django','html','css', or 'javascript'")
	
			for line in bpd['medians']:
				line.set_linewidth(4)
			locs, labels = plt.xticks()
			for label in labels:
				label.set_fontsize(20)

			plt.show()

			

	except NameError:
		pass

		





	






