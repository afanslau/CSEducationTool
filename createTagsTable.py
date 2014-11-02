from sodata.models import Posts, TaggedPosts, UniqueTags
from django.db.transaction import atomic
from django.db.models import Q

def batch_qs(qs, batch_size=1000):
	"""
	Source: 
	Returns a (start, end, total, queryset) tuple for each batch in the given
	queryset.
	
	Usage:
		# Make sure to order your querset
		article_qs = Article.objects.order_by('id')
		for start, end, total, qs in batch_qs(article_qs):
			print "Now processing %s - %s of %s" % (start + 1, end, total)
			for article in qs:
				print article.body
	"""
	total = qs.count()
	for start in range(0, total, batch_size):
		end = min(start + batch_size, total)
		yield (start, end, total, qs[start:end])


def tagFieldToList(tagstring):
	taglist = []
	if not tagstring==None and len(tagstring)>=2:
		taglist = tagstring[1:-1].split('><')
	return taglist

# Go through each post and fill tags table
# @atomic
def fillTags(posts_qs):
	missing = 0
	for p in posts_qs:
		taglist = tagFieldToList(p.tags)
		if len(taglist)==0:
			print p.id, "No Tags!"
		for ts in taglist:
			unique_tag, ut_created = UniqueTags.objects.get_or_create(tag_text=ts)
			tagged_post, tp_created = TaggedPosts.objects.get_or_create(post=p,tag=unique_tag)
			print tagged_post.id, unique_tag.id, unique_tag.tag_text, p.id


full_qs = Posts.objects.filter(~Q(tags=None)) # raw "select * from posts where tags is not null"
fillTags(full_qs)

#This batch separation routine is broken somehow...
# missing = 0
# for start, end, total, qs in batch_qs(full_qs):
# 	print "Now processing %s - %s of %s" % (start, end, total)
# 	missing += fillTags(qs)
# print missing
