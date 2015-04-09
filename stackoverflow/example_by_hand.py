terms = ['web','front','back','html','css','js','django','python','ruby','mvc']
term_index_map = {k:i for i,k in enumerate(terms)}

n_terms = len(terms)
n_users = 5
n_docs = 5

tf = np.array([
	[4,3,5,2,1,1,0,0,1,0],
	[0,0,0,10,6,11,1,1,0,0],
	[0,2,0,9,4,7,0,0,0,0],
	[0,0,0,1,0,5,1,1,4,2],
	[0,0,0,0,0,0,5,5,5,5],
	])

# Generate docs from contrived example
docs = []
for di,dv in enumerate(tf):
	wordlist = []
	for ti,freq in enumerate(dv):
		wordlist.extend([terms[ti]]*freq)
	docs[di] = ' '.join(wordlist)

