# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0003_auto_20141206_2114'),
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
            name='Resources',
        ),
        migrations.DeleteModel(
            name='TopicRelations',
        ),
        migrations.AlterField(
            model_name='topics',
            name='title',
            field=models.TextField(null=True, blank=True),
        ),
    ]
