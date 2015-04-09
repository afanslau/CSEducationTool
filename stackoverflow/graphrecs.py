from django.db.models import Q

import datetime

from scripts import loadTermMatrix as so 
from stackoverflow.models import SOUsers, SOPosts

import numpy as np 
from scipy.sparse import csr_matrix
import matplotlib.pyplot as plt

from sklearn.preprocessing import scale, normalize 
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

from operator import attrgetter

n_users=20
n_samples_per_user=100
n_terms=20
n_gram = 3

# For weekly_term prediction method
n_recent_docs = 5
n_recent_terms = 5

class KnowdGraph():
	
	params = {'wtd_doc':0.4, 'wtd_tag':0.6}

	def __init__(self, post_filter=None, vocab=None, use_tags=True):

		self.users = SOUsers.objects.all().order_by('-reputation')[:n_users] #.annotate(num_posts=Count('owned_posts'))
		self.docs = []
		self.tag_docs = []
		self.vocab=vocab

		self.tfidf_vectorizer = None

		self.doc_index_map = {}  # post.id --> index
		self.term_index_map = {} # term --> index
		self.user_index_map = {} # user.id --> index
		self.user_doc_indices = {} # user.id --> list of document indices authored by that user
		self.user_post_qs = {} # user.id --> Post queryset

		# csr_matrices
		self.wtd = None
		self.wtt = None
		self.wtu = None 


		_post_Q=~Q(tags=None)
		if post_filter is None:
			post_Q = _post_Q
		else:
			post_Q = _post_Q & post_filter
		di = 0
		ui = 0
		for u in self.users:
			print 'Get posts for user ', ui, u.id
			u_posts = SOPosts.objects.filter(post_Q, owner_user=u)[:n_samples_per_user]  #.order_by('-score')
			self.user_post_qs[u.id] = u_posts

			u_docs, user_dimap = so.vectorize_so_posts(u_posts)

			self.user_doc_indices[u.id] = set()
			for p in u_posts:
				user_doc_index = user_dimap[p.id]
				d = u_docs[user_doc_index]

				self.docs.append(d)

				tagdoc = ' '.join(p.tags.strip('><').split('><')) if p.tags is not None else ''
				self.tag_docs.append(tagdoc)

				self.doc_index_map[p.id] = di
				self.user_doc_indices[u.id].add(di)
				di += 1
			ui += 1


		# Get all posts authored by any of those users
		# sample_posts = SOPosts.objects.filter(owner_user__in=self.users)
		# print '__init__ sample_posts:  ', len(sample_posts)

		# Get docs as a list
		# docs,self.doc_index_map = so.vectorize_so_posts(sample_posts)
		# print '__init__ docs:  ', docs


		# learn vocab from tags
		if self.vocab is None:
			self.tag_count_vectorizer = CountVectorizer(stop_words='english', max_features=n_terms, binary=True)
			self.tag_matrix = self.tag_count_vectorizer.fit_transform(self.tag_docs)
			self.vocab = set(self.tag_count_vectorizer.vocabulary_.keys())

			# learn vocab from docs
			doc_vectorizer = TfidfVectorizer(stop_words='english', max_features=n_terms, min_df=0.4, max_df=0.6) # use min_df and max_df
			doc_vectorizer.fit(self.docs)
			self.vocab = self.vocab.union(set(doc_vectorizer.vocabulary_.keys()))
		self.n_terms = len(self.vocab)

		# combine to get tfidf from docs
		# wtd = docs x n-gram-features
		self.tfidf_vectorizer = TfidfVectorizer(vocabulary=self.vocab, norm='l2')
		self.doc_matrix = self.tfidf_vectorizer.fit_transform(self.docs)
		self.tag_matrix = self.tfidf_vectorizer.fit_transform(self.tag_docs)


		''' WTD Equation '''
		
		if use_tags:
			self.wtd = KnowdGraph.params['wtd_doc'] * self.doc_matrix + KnowdGraph.params['wtd_tag'] * self.tag_matrix
		else:
			self.wtd = KnowdGraph.params['wtd_doc'] * self.doc_matrix
		


		self.term_index_map = self.tfidf_vectorizer.vocabulary_
		invterm = {v:k for k,v in self.term_index_map.items()}
		self.terms = [invterm[i] for i in range(len(invterm))]


		print 'tfidf vocab: ', len(self.vocab), self.n_terms , self.vocab 

		# init Wtt as similarity matrix
		# search google for how to do this correctly
		self.wtt = (self.wtd.T * self.wtd) # multiply by transpose

		# Does this normalize by vector size? I don't think so


		# initialize a csr_matrix
		self.wtu = csr_matrix((n_users,self.n_terms))

		# init Wtu
		ui = 0		
		for u in self.users:
			# fill the matrix by...
			uv = self.get_user_vector(u)
			# print 'get_user_vector: ', uv 
			ti = 0
			print 'uv: ', uv.shape, uv
			for w in uv:
				print 'wtu[',ui,',',ti,'] : ', type(w), w
				self.wtu[ui,ti] = w
				ti+=1
			self.user_index_map[u.id] = ui
			ui+=1

			

	def get_user_vector(self, user):
		# mydocs = SOPosts.objects.filter(owner_user=user)  #improve  Select only id field
		# mydocs = [self.docs[di] for di in self.user_doc_indices[user.id]]
		# Get wtd matrix indices from the doc_index_map
		doc_indices = np.array([i for i in self.user_doc_indices[user.id]])
		# Get the wtd matrix of only documents that user interacted with

		print 
		print 'get_user_vector  doc_indices:', doc_indices

		# User has no documents that match the query. wtd = zeros
		if len(doc_indices) == 0:
			return np.array((1, n_terms))

		user_wtd = self.wtd[doc_indices,:]
		# Take the average wtd across topics (columns)
		wu = np.array(user_wtd.mean(0)).flatten() #mean returns a 1 X n_terms matrix. Convert to array and flatten to vector
		return wu



	def predict(self, context_term, user):
		# Sort all topics by relevance
		context_i = self.term_index_map[context_term]
		ui = user if type(user) is int else self.user_index_map[user.id]
		candidates = {t: self.wtt[ti,context_i] * self.wtu[ui,ti] for t,ti in self.term_index_map.items()}
		return sorted(candidates, key=candidates.get, reverse=True)




	@classmethod
	def test(cls, dt_train=None, dt_test=None):
		if dt_test is None:
			dt_test = datetime.datetime(2010,4,1)
		if dt_train is None:
			dt_train = datetime.datetime(2010,2,1)


		kg_train = KnowdGraph(Q(creation_date__lt=dt_train))


		kg_test = KnowdGraph(Q(creation_date__lt=dt_test),vocab=kg_train.vocab)


		return kg_train, kg_test


	@classmethod
	def predict_all_wtu(cls):


		# kg_train, kg_test = cls.test()
		kg_train = KnowdGraph()

		# For each user 

		ranked_prediction = {}

		for u,posts in kg_train.user_post_qs.items():
			# Find what they are learing now
			# Get the n most recent topics
			recent_posts = sorted(posts,key=attrgetter('creation_date'),reverse=True)[:n_recent_docs]
			pi = np.array([kg_train.doc_index_map[p.id] for p in recent_posts])
			recent_wtd = kg_train.wtd[pi,:]

			# Get the most important topics. Take the mean along axis 0 and argsort
			mean_wtd = np.array(recent_wtd.mean(0)).flatten()
			term_indices = np.argsort(mean_wtd)[:n_recent_terms]
			weekly_terms = [kg_train.terms[i] for i in term_indices]
			print 'user: ', u, 'weekly_terms: ', weekly_terms

			ui = kg_train.user_index_map[u]
			ranked_prediction[ui] = {}
			for t in weekly_terms:
				print 'predict: u: ',ui,' t:',t
				ranked_prediction[ui][t] = kg_train.predict(t,ui)

		return ranked_prediction


		# Recommend in context of that topic

		# Check against test set to see if we were "right"





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

