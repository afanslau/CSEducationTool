# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0005_auto_20141206_2145'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='topicrelations',
            name='from_resource',
        ),
        migrations.RemoveField(
            model_name='topicrelations',
            name='to_resource',
        ),
        migrations.DeleteModel(
            name='TopicRelations',
        ),
    ]
