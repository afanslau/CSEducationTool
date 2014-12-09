# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0004_auto_20141206_2143'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resources',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('title', models.TextField(null=True, blank=True)),
                ('text', models.TextField(null=True, blank=True)),
                ('url', models.URLField(null=True, blank=True)),
                ('child_resources', models.ManyToManyField(related_name='child_resources_rel_+', to='sodata.Resources')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TopicRelations',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('from_resource', models.ForeignKey(related_name='resources', blank=True, to='sodata.Resources', null=True)),
                ('to_resource', models.ForeignKey(related_name='parent_topics', blank=True, to='sodata.Resources', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='topics',
            name='title',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
