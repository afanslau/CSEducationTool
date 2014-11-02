# '''
# loadTermMatrix.py
# '''

# '''=== IMPORTS ===''' 
# #Python
# from time import time
# abs_t0 = time() #Time the entire script
# import itertools

# #Django
# from sodata.models import Posts, TaggedPosts, UniqueTags
# from django.db.transaction import atomic
# from django.db.models import Q

# #Other
# import numpy as np 
# from scipy import sparse,stats
# from bs4 import BeautifulSoup
# from markdown import markdown

# #Scikit-Learn
# from sklearn.preprocessing import scale, normalize 
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.feature_extraction.text import TfidfTransformer, TfidfVectorizer
# from sklearn.cluster import KMeans
# from sklearn.decomposition import PCA
# from sklearn.decomposition import TruncatedSVD

# '''===PARAMETERS==='''
# n_samples = 5 * 10 ** 4 
# log_batch_size=10 ** 3
# n_features_init = 10 ** 4
# n_features = 10 ** 3
# n_gram = 4
# title_keyword_weight = 9

# #Display params
# top_question_k = 6 #Get the top 10 data points closest to cluster center
# top_keyword_k = 15

# cluster_sizes = [5,10,50,100,200]

verbose=False



# '''=== DATA PREPROCESSING ===''' 
# '''Returns a list of document text and the mapping from the list index to their postgres post ids'''
# def vectorize_docs(n_samples = None, log_batch_size=100, verbose=True):
# 	index_map = {} # {post_id:docs_index}
# 	docs = []

# 	#Loop through all the post objects - Questions and Answers
# 	qs = Posts.objects.filter(post_type_id__in=[1])
# 	post_samples = qs if n_samples==None else qs[:n_samples]
# 	for i,question in enumerate(post_samples):  #Temporarily filter to only questions

# 		# if question.post_type_id==1: #If the post is a question, get its accepted answer
# 		# answer = question.accepted_answer
# 		# #Use accepted answer if it has one, otherwise use the top voted answer, otherwise use an empty string
# 		# if answer is None:
# 			# answer = Posts.objects.filter(parent=question).order_by('-score')
# 			# if len(answer)==0:
# 			# 	answer = ''
# 			# else:
# 			# 	answer = answer[0].body
# 		# else: 
# 		# 	answer = answer.body 
# 		#Get the most voted answer if there is one
# 		answer = ''.join([p.body for p in Posts.objects.filter(parent=question).order_by('-score')[:1]])
		
# 		#Strip markdown formatting from text ==> plain text document
# 		doc_text = title_keyword_weight*question.title +' '+ flatten_markdown(question.body) +' '+ flatten_markdown(answer)

# 		#Store the document in the list
# 		docs.append(doc_text)

# 		#Map post_id to index in docs list
# 		index_map[question.id]=i

# 		#Log progress
# 		if verbose and i%log_batch_size==0:
# 			k_log_text_preview_size = 70 #characters
# 			preview = question.title[:k_log_text_preview_size] if question.title is not None else doc_text[:k_log_text_preview_size]
# 			print('Processing question %d  %d '%(question.id,i))
# 			print('Preview:   '+preview + ' ...')
# 	return docs,index_map 
# def vectorize_tags(log_batch_size=100):
# 	def tag_tokenizer(inputString):
# 		return inputString.split(' ')

# 	docs_dict = {}  # {post_id:[t1,t2,...]}
# 	#For each post, get the tags and join them into a document
# 	for i,tp in enumerate(TaggedPosts.objects.all()):
# 		#Get tag_text
# 		tag_text = tp.tag.tag_text #Performs a query?
# 		if tp.post.id in docs_dict:
# 			docs_dict[tp.post.id].append(tag_text)
# 		else:
# 			docs_dict[tp.post.id] = [tag_text]
# 		if i%log_batch_size==0:
# 			print 'Processing row ',i,tag_text


# 	index_map = {} # {post_id:docs_index}
# 	docs = []
# 	docs_index=0
# 	for pid in list(docs_dict): #Cant change the dictionary size during iteration
# 		taglist = docs_dict.pop(pid) # No sense holding it all in memory twice
# 		docs.append(' '.join(taglist))
# 		index_map[pid] = docs_index
# 		docs_index+=1
# 	return docs,index_map
# def create_cooccurrence(td_matrix):
# 	ndocs,ntags = td_matrix.shape
# 	cooccurrence = np.zeros((ntags,ntags)) #Create an empty cooccurrence matrix
# 	for td_row in td_matrix:
# 		#Get all combinations of nonzero elements, i.e. which tags occur together in each document
# 		combs = list(itertools.combinations(td_row.nonzero()[0],2))
# 		for r,c in combs:
# 			print r,c
# 			cooccurrence[r][c] += 1
# 			cooccurrence[c][r] += 1 #Cooccurrence matrix should be symmetrical
# 	return cooccurrence


# '''===HELPER FUNCTIONS==='''
# ''' Returns the indices of the top k in sorted order  '''
# def argtopk(in_list_raw,k=10,should_sort=False):
# 	#Input Checking for correct Type and Shape
# 	inlist = in_list_raw
# 	if  type(inlist) is not np.ndarray:
# 		inlist = np.array(inlist) #Raises exception if can't convert
# 	if len(inlist.shape) != 1: raise ValueError('Array must have only one dimension')

# 	#Runs in O(n+klogk) time
# 	part = np.argpartition(inlist,-k) #Partition the array quick-sort style - get top k indices
# 	topk = part[-k:] if k>0 else part[:-k] #if k is negative, returns the minimum k elements
# 	out = topk if not should_sort else topk[np.argsort(inlist[topk])] #Sort if requested
# 	return out.tolist() if type(inlist) is list else out #Return list if original data type is a list, else np.ndarray
# ''' Inverts values for keys '''
# def invertDict(d):
# 	return {v:k for k,v in d.iteritems()}
# '''Return a pretty-printed XML string for the Element'''
# def prettify(elem):
#     rough_string = ElementTree.tostring(elem, 'utf-8')
#     reparsed = minidom.parseString(rough_string)
#     return reparsed.toprettyxml(indent="\t")
# '''#Parse tag list format  ex.    <c#><.net><string>'''
# def parse_tag_list(raw_tags):
# 	return raw_tags.strip('><').split('><')
# '''Gets all plain text from markdown format '''
# def flatten_markdown(mkd):
# 	return ''.join(BeautifulSoup(markdown(mkd)).findAll(text=True))

# 	#For each row
# 	#For each tag with value 1, find all other tags with value 1 and increment r,c in the matrix

# '''===LOAD DOCUMENTS==='''
# docs,post_index_map = vectorize_docs(n_samples=n_samples,log_batch_size=log_batch_size) #Get the doc bodies
# n_samples = len(docs) #If there are less than the requested n_samples in the database, set it to the correct size
# index_post_map = invertDict(post_index_map)
# # title_docs = [ Posts.objects.get(id=index_post_map[i]).title for i in range(n_samples) ] #Get the titles
# # docs = [ title_keyword_weight*(title_docs[i] + ' ') + body_docs[i]  for i in range(n_samples)] #Repeat the title and concat the body


# '''===PROCESS DATA==='''
# # #Log progress
# print 'Generating Tf-idf'
# #Use tfidf
# t0 = time()
# tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features = n_features_init,ngram_range=(1,n_gram),max_df=0.8)
# tfidf_matrix_raw = tfidf_vectorizer.fit_transform(docs) #docs x n-gram-features
# elapsed_tfidf = time() - t0
# print 'Generating Tf-idf for ', tfidf_matrix_raw.shape, ' posts X n-grams'
# print 'Finished in %0.3f seconds' % elapsed_tfidf

# #Mean normalization and unit variance
# '''http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.scale.html#sklearn.preprocessing.scale'''
# print 'Scale matrix'
# t0 = time()
# tfidf_matrix_scaled = scale(tfidf_matrix_raw, with_mean = False) #Can't use sparse matrices unless with_mean=False
# elapsed_scale = time() - t0
# print 'Finished scaling in %0.3f seconds' % elapsed_scale


# '''
# Dimensionality reduction

# TruncatedSVD is very similar to PCA, but differs in that it works on sample matrices X directly instead of their covariance matrices.
# When the columnwise (per-feature) means of X are subtracted from the feature values, 
# 	truncated SVD on the resulting matrix is equivalent to PCA. In practical terms,
# 	this means that the TruncatedSVD transformer accepts scipy.sparse matrices without the need to densify them,
# 	as densifying may fill up memory even for medium-sized document collections.
# '''
# print 'Performing Dimensionality Reduction with LSA Latent Semantic Analysis (SVD Singular Value Decomposition)  n_features = ', n_features
# t0 = time()
# svd = TruncatedSVD(n_features)
# X = normalize(svd.fit_transform(tfidf_matrix_scaled))
# elapsed_dimension = time() - t0
# print 'Finished Dimensionality Reduction in %0.3f seconds' % elapsed_dimension


'''===Perform clustering with different n_clusters and compare results==='''
for n_clusters in cluster_sizes:
	outfilename = 'n_clusters_%d.txt'%n_clusters

	km = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=1000, n_init=1, verbose=False)
	print('Clustering data with %s clusters' % n_clusters)
	t0 = time()
	X_clust_dist = km.fit_transform(X)
	elapsed_clustering = time() - t0
	print 'Finished clustering in %0.3fs' % elapsed_clustering

	#Get Dendrogram
	#http://scikit-learn.org/stable/modules/clustering.html
	#http://stackoverflow.com/questions/11917779/how-to-plot-and-annotate-hierarchical-clustering-dendrograms-in-scipy-matplotlib



	#Get the post objects for each data point in the cluster
	#Write them to a file

	with open(outfilename,'w') as f:
		#For Each Cluster
		for cluster_i in range(n_clusters):
			verbose = (cluster_i+1)%10==0

			f.write('B========== CLUSTER '+str(cluster_i)+' ==========\n\n')

			#Get all points in cluster i
			X_ci_dist = X_clust_dist[:,cluster_i] #Cluster i's distances

			#Write the most popular keywords - i.e. topk of tfidf within the cluster
			ix_in_cluster = np.where(km.labels_==cluster_i)[0]

			#Get all columns of X for rows in_cluster_i
			#http://stackoverflow.com/questions/10989438/how-to-cleanly-index-numpy-arrays-with-arrays-or-anything-else-that-supports-ad
			X_in_cluster = X[ix_in_cluster,:]
			full_docs_in_cluster = [docs[i] for i in ix_in_cluster]

			#Get the indices of columns (keywords) that have non-zero elements in at least one row (posts)
			#This elminates any keywords that are not used in that cluster
			#Need to get the idf WITHIN the cluster (not tfidf_vectorizer._tfidf.idf_ because this is global idf)

			#Keywords 
			if verbose: print('Generating tfidf within cluster %d' % cluster_i)
			t0_in_cluster = time()
			tfidf_in_cluster = TfidfVectorizer(stop_words='english', max_features = n_features*10,ngram_range=(1,n_gram),max_df=0.8)
			X_in_cluster = tfidf_in_cluster.fit_transform(full_docs_in_cluster)
			vocab_ix_map_in_cluster = tfidf_in_cluster.vocabulary_
			ix_vocab_map_in_cluster = invertDict(vocab_ix_map_in_cluster)
			relevance_in_cluster = np.array(X_in_cluster.sum(0)).flatten() #sum over columns returns a matrix, convert to 1darray
			#Get topk keywords in cluster
			top_keywords_in_cluster = [ix_vocab_map_in_cluster[i] for i in argtopk(relevance_in_cluster,top_keyword_k,should_sort=True)] #Get the minimum idf keywords
			elapsed_in_cluster = time() - t0_in_cluster
			if verbose: print('Finished idf_within_cluster in %0.3fs' % elapsed_in_cluster)

			f.write('Top %d keywords:  (Measured by sum of tfidf along documents within this cluster\n' % top_keyword_k)
			for kw in top_keywords_in_cluster:
				f.write('\t%s\n' % kw.encode('utf-8'))


			#Stats
			f.write('\n\nDistance Statistics:\n'  )
			#Calculate statistics
			z = stats.zscore(X_clust_dist[ix_in_cluster,cluster_i])
			maxz = z.max()
			minz = z.min()
			outlier_diff = (abs(z) - np.tile(2,z.shape))
			outliers = z[np.where(outlier_diff > 0)]
			#Display output
			f.write('\tMean distance to cluster center: %0.5f\n' % X_clust_dist.mean())
			f.write('\tStandard deviation of distance to cluster center: %0.5f\n' % X_clust_dist.std())
			f.write('\tMax zscore: %0.2f\n' % z.max())
			f.write('\tMin zscore: %0.2f\n' % z.min())
			f.write('\tn_outliers(|z|>2): %d\n' % outliers.size)
			# f.write('\tOutlier z-scores: %s\n' % str(outliers))


			#Top Questions
			#Calculate 
			#top question indices
			tqi = argtopk(X_ci_dist, -top_question_k, should_sort=True).tolist() #Need minimum of X_ci_dist
			#post_ids
			pids = [index_post_map[i] for i in tqi]  
			#l[::-1] reverses the array l.reverse() in place, reversed(l) returns an iterator
			#l[::-1] is fastest in general http://stackoverflow.com/questions/3705670/best-way-to-create-a-reversed-list-in-python

			#Query database for those questions
			top_qs = Posts.objects.filter(id__in=pids)  #Needs to be in same order as pids
			#Sort these results in the same order as pids  -  Distance 
			top_qs = list(top_qs) #QuerySet is small enough to execute
			top_qs.sort(key=lambda post: pids.index(post.id)) #Sort in place in the same order as pids

			#Display
			f.write('\n\n-----Closest %d questions in cluster-----\n\n' % top_question_k)
			#For each of the top_question_k data points
			for rank,p in enumerate(top_qs): #for each post
				#Get Distance of each point
				doc_i = post_index_map[p.id]
				dist = X_ci_dist[doc_i]
				#Write rank, distance, title, tags
				f.write('Title: %s\n' % p.title.encode('utf-8'))
				f.write('\tId: %d\n' % p.id)
				f.write('\tRank: %d  -  Distance: %3.5f\n' % (rank, dist))
				f.write('\tTags: %s\n' % ', '.join(parse_tag_list(p.tags)).encode('utf-8'))
				f.write('\tBody: %s\n\n' % flatten_markdown(p.body)[:140].encode('utf-8'))


			#Bottom Questions - Get the max distance within the cluster
			
			#Returns index of doc in ix_in_cluster. Need to map back to original doc space
			amax_temp = argtopk(X_ci_dist[ix_in_cluster], top_question_k, should_sort=True)
			#Map to original doc index and get pids
			pids = [index_post_map[i] for i in ix_in_cluster[amax_temp]]
			bottom_qs = list(Posts.objects.filter(id__in=pids))
			bottom_qs.sort(key=lambda post: pids.index(post.id)) #Sort in place in the same order as pids

			#Display
			f.write('\n\n-----Furthest %d questions in cluster-----\n\n' % top_question_k)
			#For each of the top_question_k data points
			for rank,p in enumerate(bottom_qs): #for each post
				#Get Distance of each point
				doc_i = post_index_map[p.id]
				dist = X_ci_dist[doc_i]
				#Write rank, distance, title, tags
				f.write('Title: %s\n' % p.title.encode('utf-8'))
				f.write('\tId: %d\n' % p.id)
				f.write('\tRank: %d  -  Distance: %3.5f\n' % (rank, dist))
				f.write('\tTags: %s\n' % ', '.join(parse_tag_list(p.tags)).encode('utf-8'))
				f.write('\tBody: %s\n\n' % flatten_markdown(p.body)[:140].encode('utf-8'))


			f.write('\n\nE========== CLUSTER '+str(cluster_i)+' ==========\n\n')
	print 'Finished clustering for n_clusters=%d in %0.3fs' % (n_clusters, time()-t0)


# print 'Perform PCA k=2'
# t0=time()
# pca = PCA(n_components=2)
# X_new = pca.fit_transform(X)
# elapsed_pca = time() - t0
# print 'Finished PCA in %0.3fs' % elapsed_pca
# explained_var = pca.explained_variance_ratio_

abs_elapsed = time() - abs_t0
print 'Emtire script took %0.3f s to run' % abs_elapsed



