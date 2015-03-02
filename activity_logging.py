import json
from sodata.models import Resources, TopicRelations
from django.contrib.auth.models import User

class LogEncoder(json.JSONEncoder):
    def default(self, o):
		try:
			if hasattr(o, 'username') and hasattr(o, 'id'):
				return {'id':o.id, 'username':o.username}
			elif type(o) is Resources:
				return {'id':o.id,'title':o.title, 'url':o.url}
			elif type(o) is TopicRelations:
				return {'parent_resource':self.default(o.from_resource), 'child_resource':self.default(o.to_resource)}
			else:
				return o.__dict__
		except:
			return o.__dict__
event_types = {
	'register':['user'],
	'login':['user'],
	'logout':['user'],
	'create_resource':['user','resource','parent_resource'],
	'update_resource':['user','resource','parent_resource'],
	'delete_resource':['user','resource','parent_resource'],
	'create_relation':['user','parent_resource','child_resource'],
	'delete_relation':['user','parent_resource','child_resource'],
	'accept_recommendation':['user','parent_resource','child_resource'],
	'reject_recommendation':['user','parent_resource','child_resource'],
	'traverse_path':['user','source_resource','destination_resource'],
	'other':[],
}



