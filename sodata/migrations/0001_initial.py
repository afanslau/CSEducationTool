# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Resources',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('title', models.TextField(null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('url', models.URLField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TopicRelations',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Topics',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('title', models.TextField(null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('children', models.ManyToManyField(related_name='children_rel_+', null=True, to='sodata.Topics', blank=True)),
                ('parents', models.ManyToManyField(related_name='parents_rel_+', null=True, to='sodata.Topics', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='topicrelations',
            name='from_node',
            field=models.ForeignKey(related_name='to_node', to='sodata.Topics'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='topicrelations',
            name='to_node',
            field=models.ForeignKey(related_name='from_node', to='sodata.Topics'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resources',
            name='topic',
            field=models.ForeignKey(blank=True, to='sodata.Topics', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='AuthGroup',
            fields=[
            ],
            options={
                'db_table': 'auth_group',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AuthGroupPermissions',
            fields=[
            ],
            options={
                'db_table': 'auth_group_permissions',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AuthPermission',
            fields=[
            ],
            options={
                'db_table': 'auth_permission',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AuthUser',
            fields=[
            ],
            options={
                'db_table': 'auth_user',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AuthUserGroups',
            fields=[
            ],
            options={
                'db_table': 'auth_user_groups',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AuthUserUserPermissions',
            fields=[
            ],
            options={
                'db_table': 'auth_user_user_permissions',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
            ],
            options={
                'db_table': 'comments',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DjangoAdminLog',
            fields=[
            ],
            options={
                'db_table': 'django_admin_log',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DjangoContentType',
            fields=[
            ],
            options={
                'db_table': 'django_content_type',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DjangoMigrations',
            fields=[
            ],
            options={
                'db_table': 'django_migrations',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DjangoSession',
            fields=[
            ],
            options={
                'db_table': 'django_session',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Posts',
            fields=[
            ],
            options={
                'db_table': 'posts',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaggedPosts',
            fields=[
            ],
            options={
                'db_table': 'tagged_posts',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UniqueTags',
            fields=[
            ],
            options={
                'db_table': 'unique_tags',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
            ],
            options={
                'db_table': 'users',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Votes',
            fields=[
            ],
            options={
                'db_table': 'votes',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
