# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0012_auto_20141208_0422'),
    ]

    operations = [
        migrations.AddField(
            model_name='resources',
            name='pre_seeded',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='topicrelations',
            name='from_resource',
            field=models.ForeignKey(related_name=b'child_resources', to='sodata.Resources'),
        ),
        migrations.AlterField(
            model_name='topicrelations',
            name='to_resource',
            field=models.ForeignKey(related_name=b'parent_resources', to='sodata.Resources'),
        ),
    ]
