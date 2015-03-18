import numpy as np
from numpy.linalg import norm
from scipy import sparse 
from sklearn.preprocessing import scale, normalize 
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel

from sodata.models import Resources, TfidfMatrix

from django.db import transaction
from django.db.models import Max
from django.core.exceptions import ObjectDoesNotExist

from sklearn.externals import joblib

import os
# from CSEducationTool.settings import BASE_DIR
from django.conf import settings

BASE_DIR = settings.BASE_DIR

log_batch_size=10 ** 3
k_log_text_preview_size = 70 #characters


n_features_init = 10 ** 4
n_features = 10 ** 3
n_gram = 4
title_keyword_weight = 9



'''=== DATA PREPROCESSING ===''' 
'''Returns a list of document text and the mapping from the list index to their postgres post ids'''
def vectorize_docs(n_samples = None, log_batch_size=100, verbose=True, qs=None):
	index_map = {} # {post_id:docs_index}
	docs = []

	#Loop through all the post objects - Questions and Answers
	if qs is None:
		qs = Resources.objects.all()
	samples = qs if n_samples==None else qs[:n_samples]


	for i,sample in enumerate(samples):  #Temporarily filter to only questions
		_title = sample.title if sample.title is not None else '' 
		_text = sample.text if sample.text is not None else '' 
		doc_text = title_keyword_weight*_title +' '+ _text

		#Store the document in the list
		docs.append(doc_text)

		#Map post_id to index in docs list
		index_map[sample.id]=i

		#Log progress
		if verbose and i%log_batch_size==0:
			preview = sample.title[:k_log_text_preview_size] if sample.title is not None else doc_text[:k_log_text_preview_size]
			print('Processing sample %d  %d '%(sample.id,i))
			print('Preview:   '+preview + ' ...')
	return docs,index_map 


# Lazy loading
cached_tfidf_vectorizer = None
index_vocab_map = None
def get_tfidfvectorizer(train=False):
	global cached_tfidf_vectorizer
	global index_vocab_map
	_train = train 
	if cached_tfidf_vectorizer is None:
		try:
			cached_tfidf_vectorizer = joblib.load( os.path.join(BASE_DIR,'data_cache','cached_tfidf_vectorizer.pkl'))
			index_vocab_map = joblib.load(os.path.join(BASE_DIR,'data_cache','index_vocab_map.pkl'))
		except IOError:
			_train = True
	if _train:
		# Train Tf-Idf with all Resources
		cached_tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features = n_features_init,ngram_range=(1,n_gram),max_df=0.8, norm='l2')
		docs,id_index_map = vectorize_docs()
		cached_tfidf_vectorizer.fit(docs)
		joblib.dump(cached_tfidf_vectorizer, os.path.join(BASE_DIR,'data_cache','cached_tfidf_vectorizer.pkl'))
		index_vocab_map = invertDict(cached_tfidf_vectorizer.vocabulary_)
		joblib.dump(index_vocab_map, os.path.join(BASE_DIR,'data_cache','index_vocab_map.pkl'))


	return cached_tfidf_vectorizer


# Returns a similarity matrix with the given resources
def get_similarity(*resources):
	if resources is None:
		_resources = Resources.objects.all()
	else:
		_resources = resources
	# Get the vectors for each resource
	docs = [r.text if r.text is not None else '' for r in _resources]
	text_vectors = get_tfidfvectorizer().transform(docs)
	similarity = linear_kernel(text_vectors) # Dots the matrix with itself, outputs array([[1, similarity],[similarity,1]])
	return similarity









'''===HELPER FUNCTIONS==='''
''' Returns the indices of the top k in sorted order  '''
def argtopk(in_list_raw,k=10,should_sort=False):
	if k > len(in_list_raw) or k < 1-len(in_list_raw):
		return sorted(in_list_raw) if should_sort else in_list_raw
	#Input Checking for correct Type and Shape
	inlist = in_list_raw
	if  type(inlist) is not np.ndarray:
		inlist = np.array(inlist) #Raises exception if can't convert
	if len(inlist.shape) != 1: raise ValueError('Array must have only one dimension')

	#Runs in O(n+klogk) time
	part = np.argpartition(inlist,-k) #Partition the array quick-sort style - get top k indices
	topk = part[-k:] if k>0 else part[:-k] #if k is negative, returns the minimum k elements
	out = topk if not should_sort else topk[np.argsort(inlist[topk])] #Sort if requested
	return out.tolist() if type(inlist) is list else out #Return list if original data type is a list, else np.ndarray
''' Inverts values for keys  --  should only be used with one to one mappings '''
def invertDict(d):
	return {v:k for k,v in d.iteritems()}
'''Return a pretty-printed XML string for the Element'''





# res = Resources.objects.all()
# r1 = res[10]
# r2 = res[11]

# print r1.title
# print r2.title 
# print get_similarity((r1))




# @transaction.atomic
# def store_vectors(resources=None, train=False):
# 	# Clear matrix if retraining
# 	if train: 
# 		TfidfMatrix.objects.all().delete()
# 	# Get the resources to be added
# 	if resources is None:
# 		resources = Resources.objects.filter(tfidf_vector=None)

# 	# Get list of raw text
# 	docs,id_index_map = vectorize_docs(qs=resources)

# 	# Transform through tfidf
# 	tfidf_vectorizer = get_tfidfvectorizer(train=train)
# 	tfidf_matrix_raw = tfidf_vectorizer.transform(docs) #docs x n-gram-features
# 	tfidf_matrix = scale(tfidf_matrix_raw, with_mean = False) #Can't use sparse matrices unless with_mean=False
# 	index_vocab_map = invertDict(tfidf_vectorizer.vocabulary_)


# 	# Create or update TfidfMatrix entries in the database
# 	# Create for new resoruces,  update for edited resources 


# 	# resources = Resources.objects.filter(id__in=id_index_map.keys())
# 	n = len(resources)
# 	for i,r in enumerate(resources):
# 		doc_ix = id_index_map[r.id]
# 		print ('tfidf for resource '+str(i)+' of '+str(n)+' : '+r.title)

# 		nonzero_cols = tfidf_matrix[doc_ix,:].nonzero()[1]
# 		for vocab_ix in nonzero_cols:
# 			tfidf = tfidf_matrix[doc_ix, vocab_ix]
# 			term = index_vocab_map[vocab_ix]
# 			try:
# 				entry = TfidfMatrix.objects.get(resource=r, term=term)
# 			except ObjectDoesNotExist:
# 				entry = TfidfMatrix(resource=r, term=term)
# 			entry.row = doc_ix
# 			entry.col = vocab_ix
# 			entry.tfidf = tfidf
# 			entry.save()








