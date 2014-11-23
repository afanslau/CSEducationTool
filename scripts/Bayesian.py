from scripts.loadTermMatrix import *

from sklearn.feature_extraction.text import CountVectorizer

#Graph Library
from networkx import DiGraph
import matplotlib as plt 


n_features_default = 1000
class Bayesian(object):
	"""Creates a hierarchy from conditional co-occurrance probabilities"""

	def __init__(self, docs, n_features=n_features_default):
		"""  """
		super(Bayesian, self).__init__()
		self.docs = docs
		self.n_features = n_features
		print 'Counting...'
		self.vectorizer = TfidfVectorizer(stop_words='english', max_features = n_features,ngram_range=(1,3),max_df=0.6)
			#CountVectorizer(stop_words='english', max_features=self.n_features, ngram_range=(1,3))
		self.vectors = self.vectorizer.fit_transform(self.docs)
		self.vocabulary = self.vectorizer.vocabulary_
		print 'Getting Condi... ', self.vectors.shape
		self.condi = self.init_conditional_matrix()
		print 'Building Graph...'
		self.network = self.init_graph()

	def init_graph(self):
		#Represent the graph using adjacency lists
		g = DiGraph()
		g.add_nodes_from(self.vocabulary) #The keys (terms) become nodes in the graph
		for x in self.vocabulary:
			for y in self.vocabulary:
				if self.conditional_probability(x,y) >= 0.8 and self.conditional_probability(y,x) < 0.8:
					g.add_edge(x,y)
		return g 
	def conditional_probability(self,x,y):
		try:
			i = self.vocabulary[x]
			j = self.vocabulary[y]
			return self.condi[i,j]
		except KeyError:
			return None
	def init_conditional_matrix(self):
		#For each term
		#Get the condi for every other term
		n_features=self.n_features
		condi = np.zeros((n_features,n_features))
		for i in range(n_features):
			for j in range(i,n_features):
				condi[i,j] = self.conditional_probability_indx(i,j)
				print 'condi[',i,',',j,'] = ',condi[i,j]

		return condi 
	def conditional_probability_indx(self,i, j):
		"""Returns the conditional_probability P(x|y) where x and y correspond to indices i,j in docs_data"""
		if i==j: return 1
		'''Find all documents with y in it, then get P(x) = len(x in D_y)/len(D_y)'''	
		data = self.vectors
		#Get the subset of documents where term y occurs
		D_y = data[np.nonzero(data[:,j])[0]]
		if D_y.shape[0]==0: return 0
		#Get the subset of documents where term x occurs in D_y
		D_xy = D_y[np.nonzero(D_y[:,i])[0]]
		return D_xy.shape[0]/float(D_y.shape[0])
	def get_root(self):
		g = self.network
		for connected in nx.connected_components(g.to_undirected()):
			unvisited = set(connected)
			#Start by choosing a vertex from the unvisited set
			#then traverse the graph marking
			while len(unvisited)>0:
				candidate = unvisited.pop()
				stack = [candidate]
				#Do dfs with that source
				while len(stack)>0:
					v = stack.pop() #Pop node
					if v in unvisited: unvisited.remove(v) #Visit node 
					for w in g.edges(v): #Push children if unvisited
						if w in unvisited:
							stack.append(w)
			yield candidate

