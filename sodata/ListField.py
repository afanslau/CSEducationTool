'''
Source:  http://stackoverflow.com/questions/5216162/how-to-create-list-field-in-django
'''

from django.db import models

class ListField(models.TextField):
    __metaclass__ = models.SubfieldBase
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value

        return value.strip('><').split('><')

    def get_prep_value(self, value):
        if value is None:
            return value
        out = ''
        for v in value:
            out += u'<'+unicode(v)+u'>'
        return out

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)