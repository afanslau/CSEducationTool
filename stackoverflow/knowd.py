from django.db.models import Q

import datetime

from scripts import loadTermMatrix as so 
from stackoverflow.models import SOUsers, SOPosts

import numpy as np 
from scipy.sparse import csr_matrix
import matplotlib.pyplot as plt

from sklearn.preprocessing import scale, normalize 
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics import average_precision_score

from operator import attrgetter



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
		

		# Fields
		self.tfidf_vectorizer = None

		# Data Structures
		self.term_index_map = {} # term --> term_index
		

		# Database references
		self.doc_index_map = {}  # post.id --> doc_index
		self.user_index_map = {} # user.id --> user_index
		

		# Data
		self.docs = [] # Docs
		self.terms = []
		self.tag_docs = [] # Tag lists - for stackoverflow, assumed to be tags created by the author
		self.user_doc_indices = {} # user_index --> set of associated documents
		self.vocab = set() # Terms


		# csr_matrices
		self.wtd = None
		self.wtt = None
		self.wtu = None 




	def train_with_so(self, q_post=None, so_users=None, n_users=20, n_samples_per_user=100, vocab=None):

		# Set variables
		_post_Q=~Q(tags=None)
		if q_post:			
			post_Q = _post_Q & q_post
		else:
			post_Q = _post_Q


		# Fetch users
		if so_users:
			self.so_users = so_users
		else:
			self.so_users = SOUsers.objects.all().order_by('-reputation')[:n_users] #.annotate(num_posts=Count('owned_posts'))
		self.n_users = len(self.so_users)

		# Fetch posts for each user
		for ui,u in enumerate(self.so_users):
			# Get posts for this user
			print 'Get posts for user ', ui, u.id
			u_posts = SOPosts.objects.filter(post_Q, owner_user=u).order_by('-creation_date')[:n_samples_per_user]  #.order_by('-score')

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


		# Get all posts authored by any of those users
		# sample_posts = SOPosts.objects.filter(owner_user__in=self.users)
		# print '__init__ sample_posts:  ', len(sample_posts)

		# Process data
		if vocab:
			self.vocab = vocab
		self.learn_weights()

	def train_with_example(self):
		terms = ['web','front','back','html','css','js','django','python','ruby','mvc']
		unrelated = ['algorithms','tcp','recursion','unix','graphics','cpu']
		term_index_map = {k:i for i,k in enumerate(terms)}

		n_terms = len(terms)
		n_users = 3
		n_docs = 5

		tf = np.array([
			[4,3,5,2,1,1,0,0,1,0],		# Overview doc
			[0,0,0,10,6,11,1,1,0,0],	# Back & Front
			[0,2,0,9,4,7,0,0,0,0],		# mostly front
			[0,0,0,1,0,5,1,1,4,2],		# mostly back
			[0,0,0,0,0,0,5,5,5,5],		# all back
			])

		# Generate docs from contrived example
		docs = []
		for di,dv in enumerate(tf):
			wordlist = []
			for ti,freq in enumerate(dv):
				wordlist.extend([terms[ti]]*freq)
			docs.append(' '.join(wordlist))



		user_doc_indices = {
			0:[0], 	# Overview poster
			1:[1,2],  # Well rounded user
			2:[3,4]	# Back, learning some front
		}


		self.train_with_data(docs=docs, vocab=set(terms), user_doc_indices=user_doc_indices, use_tags=False)




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
			self.vocab = self.vocab.union(set(doc_vectorizer.vocabulary_.keys()))
		self.n_terms = len(self.vocab) # this is wrong. need to limit to n_terms. n_terms should be immutable 

		
		# Fit & Transform with self.vocab
		self.tfidf_vectorizer = TfidfVectorizer(vocabulary=self.vocab, norm='l2')
		self.doc_matrix = self.tfidf_vectorizer.fit_transform(self.docs)
	
		self.term_index_map = self.tfidf_vectorizer.vocabulary_
		invterm = {v:k for k,v in self.term_index_map.items()}
		self.terms = [invterm[i] for i in range(len(invterm))]



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

		# ui = 0		
		# for u in self.users:
		# 	# fill the matrix by...
		# 	uv = self.get_user_vector(u)
		# 	# print 'get_user_vector: ', uv 
		# 	ti = 0
		# 	print 'uv: ', uv.shape, uv
		# 	for w in uv:
		# 		print 'wtu[',ui,',',ti,'] : ', type(w), w
		# 		self.wtu[ui,ti] = w
		# 		ti+=1
		# 	self.user_index_map[u.id] = ui
		# 	ui+=1

			

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






	def predict(self, context_term, user, baseline=False):
		# Sort all topics by relevance
		context_i = context_term if type(context_term) is int else self.term_index_map[context_term]
		ui = user if type(user) is int else self.user_index_map[user.id]
		user_param = [1]*self.n_terms if baseline else [self.wtu[ui,ti] for ti in range(self.n_terms)]
		return np.array([self.wtt[ti,context_i] * user_param[ti]  for ti in range(self.n_terms)])

	def predict_all(self, baseline=False):

		# For each user 
		topic_prediction = np.zeros((self.n_users, self.n_terms))
		# ranked_prediction = {}

		for ui in range(self.n_users):



			# Get what their favorite topic has been recently

			# Use only the most recent documents to get the recent_wtu
			# Sort by doc index and take the top n  -  docs are already sorted by (-user.reputation, -post.creation_date)    
			recent_docs_i = np.array(sorted(self.user_doc_indices[ui])[:self.n_recent_docs])
			recent_wtd = self.wtd[recent_docs_i,:]

			# Get the most important topics. Take the mean along axis 0 and argsort
			recent_wtu = np.array(recent_wtd.mean(0)).flatten()
			fav_term = np.argsort(recent_wtu)[::-1][0] #  [:self.n_recent_terms]

			predicted_terms = self.predict(context_term=self.terms[fav_term],user=ui, baseline=baseline)

			print 'user: ', ui, 'predicted_terms: ', [self.terms[ti] for ti in np.argsort(predicted_terms)[::-1][:5]]

			topic_prediction[ui,:] = predicted_terms



		return topic_prediction



	def compare_to_test(self, kg_test, baseline=False):
		y_true = np.array(kg_test.wtu.todense())
		nz = y_true.nonzero()
		nz_mean = y_true[nz[0], nz[1]].mean()
		nz_std = y_true[nz[0], nz[1]].std()
		thrsh = nz_mean + nz_std


		y_true =  (y_true > thrsh) *1.  # Convert from Boolean to Float
		y_score = self.predict_all(baseline=baseline)

		mean_avg = np.array([average_precision_score(y_true[u,:],y_score[u,:]) for u in range(self.n_users)])
		return mean_avg

		# Recommend in context of that topic

		# Check against test set to see if we were "right"

	def get_test_results(self, kg_test):
		self.compare_to_test(kg_test)


	@classmethod
	def train_test_with_so(cls, q_train=None, q_test=None, n_terms=500, n_users=100):
		if q_train is None:
			q_train = Q(creation_date__lt=datetime.datetime(2010,2,1))
		if q_test is None:
			q_train = Q(creation_date__lt=datetime.datetime(2010,4,1))		


		# Train two graphs with different data sets
		kg_train = KnowdGraph(n_terms=n_terms)
		kg_train.train_with_so(q_post=q_train, n_users=n_users)
		kg_test = KnowdGraph()
		kg_test.train_with_so(q_post=q_test, n_users=n_users,vocab=kg_train.vocab)
		return kg_train, kg_test





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

def run():
	'training...'
	kg_train, kg_test = KnowdGraph.train_test_with_so(n_terms=50, n_users=10)
	'testing...'
	precision = kg_train.compare_to_test(kg_test)
	print 'Precision: ', precision
	return kg_train, kg_test, precision

if __name__ == '__main__':
	# import sys

	# print sys.argv

	# if len(sys.argv) > 2:
	# 	n_terms = sys.argv[2]
	# else:
	# 	n_terms = 50

	# if len(sys.argv) > 1:
	# 	n_users = sys.argv[1]
	# else:
	# 	n_users = 10
	try: 
	# This is supposedly bad practice (to test for the existince of a variable), but for a script I don't see a disadvantage yet 
	# http://stackoverflow.com/questions/843277/how-do-i-check-if-a-variable-exists-in-python
		if run_now:
			print 'training...'
			n_users = 3
			n_train_samples = 50
			n_test_samples = 200

			kg_train = KnowdGraph()
			kg_train.train_with_so(n_users=n_users, n_samples_per_user=n_train_samples)

			kg_test = KnowdGraph()
			kg_test.train_with_so(n_users=n_users, n_samples_per_user=n_test_samples, vocab=kg_train.vocab)

			print 'testing...'
			precision = kg_train.compare_to_test(kg_test)
			baseline_precision = kg_train.compare_to_test(kg_test, baseline=True)
			precision_mean = precision.mean()
			print 'Precision: ', , precision
			print 'Baseline Precision: ', baseline_precision.mean(), baseline_precision

			print 'Percent Difference', 



	except NameError:
		pass

		



	






