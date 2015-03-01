import watson
from sodata.models import Resources

fr = watson.filter(Resources, 'django')

print "before"
for r in fr:
    print r.watson_rank, "--" , r.title
    if r.user_relations.get(user__username='adam').starred:
            r.watson_rank *= 7

print "after"
for r in fr:
    print r.watson_rank, "--" , r.title
