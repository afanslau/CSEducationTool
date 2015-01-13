from sodata.models import UserRelation
from django.contrib.auth.models import User
from django.db.models import Q

u = User.objects.get(username="adam")
ur = UserRelation.objects.filter(~Q(user_type=1), user=u)
tot = len(ur)
for i,r in enumerate(ur):
	print i, 'of', tot, r.id
	r.user_type = 1
	r.save()
