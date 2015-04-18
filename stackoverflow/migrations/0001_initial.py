# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SOTaggedPosts',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'tagged_posts',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SOComments',
            fields=[
            ],
            options={
                'db_table': 'comments',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SOPosts',
            fields=[
            ],
            options={
                'db_table': 'posts',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sotaggedposts',
            name='post',
            field=models.ForeignKey(db_column='post_id', blank=True, to='stackoverflow.SOPosts', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='SOUniqueTags',
            fields=[
            ],
            options={
                'db_table': 'unique_tags',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sotaggedposts',
            name='tag',
            field=models.ForeignKey(db_column='tag_id', blank=True, to='stackoverflow.SOUniqueTags', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='SOUsers',
            fields=[
            ],
            options={
                'db_table': 'users',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sotaggedposts',
            name='user',
            field=models.ForeignKey(db_column='user_id', blank=True, to='stackoverflow.SOUsers', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='SOVotes',
            fields=[
            ],
            options={
                'db_table': 'votes',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
