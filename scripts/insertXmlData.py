from time import time
abs_t0 = time() #Time the entire script
import itertools

#Django
from CSEducationTool.sodata.models import Posts, TaggedPosts, UniqueTags

#xml
import xml.etree.ElementTree as etree


# These constants should really be in settings.py
PTYPE_QUESTION = 1
PTYPE_ANSWER = 2

xmL = '/Users/afanslau/Desktop/Thesis/cs.stackexchange.com/Posts.xml'
nslice = 7000000 #set nslice to an integer to parse only a portion of the file
fullXml = etree.iterparse(xmL)
rowIterator = fullXml if nslice is None else itertools.islice(fullXml,0,nslice)



#For each row in the xml file, insert into database


def vectorize_xml(rowIterator, db_insert=False):
	index_map = {} # {post_id:docs_index}
	docs = []

	print_batch = 100
	for i, (event, elem) in enumerate(rowIterator):
		#Parse the xml row into a django Post object
		p = Posts()
		#Why am I getting a key error on the last row?
		#KeyError: 'PostTypeId'
		ptype = elem.attrib['PostTypeId']
		p.post_type_id = int(ptype)
		
		#How do I add these fields and keep foreign key constraints??
		# p.parent
		# p.accepted_answer

		p.body = elem.attrib['Body']
		preview = p.body[:100]
		if p.post_type_id == PTYPE_QUESTION:
			p.tags = elem.attrib['Tags']		
			#Create a unique_tags entry and a tagged_posts entry
			p.title = elem.attrib['Title']
			preview = p.title[:100]
		p.score = elem.attrib['Score']
		p.id = elem.attrib['Id']


		answer = '' #.join([p.body for p in Posts.objects.filter(parent=question).order_by('-score')[:1]])
		title = p.title
		if title is None: title = ''
		#Strip markdown formatting from text ==> plain text document
		doc_text = title_keyword_weight*title +' '+ flatten_markdown(p.body) +' '+ flatten_markdown(answer)

		#Store the document in the list
		docs.append(doc_text)

		#Map post_id to index in docs list
		index_map[p.id]=i

		#Log progress
		if verbose and i%log_batch_size==0:
			k_log_text_preview_size = 70 #characters
			preview = p.title[:k_log_text_preview_size] if p.title is not None else doc_text[:k_log_text_preview_size]
			print('Processing p %d  %d '%(p.id,i))
			print('Preview:   '+preview + ' ...')
	

	if db_insert:
		p.save()
		

	if i%print_batch==0:
		print i, preview

	return docs,index_map 

	
