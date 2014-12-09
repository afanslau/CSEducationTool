from django.db import models
import datetime
class AutoUpdateDateTimeField(models.DateTimeField):

	# Set default value to now
	# def __init__(self, *args, **kwargs):
	#     if 'default' not in kwargs:
	#         kwargs['default'] = timezone.now
	#     super(AutoDateTimeField, self).__init__(*args, **kwargs)


	# Update the field each time it saves
    def pre_save(self, model_instance, add):
        return datetime.datetime.now()
