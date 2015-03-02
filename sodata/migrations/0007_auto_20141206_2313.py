# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0006_auto_20141206_2306'),
    ]

    operations = [
        migrations.CreateModel(
            name='TopicRelations',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('from_resource', models.ForeignKey(related_name='child_resources', blank=True, to='sodata.Resources', null=True)),
                ('to_resource', models.ForeignKey(related_name='parent_topics', blank=True, to='sodata.Resources', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='resources',
            name='child_resources',
        ),
    ]
