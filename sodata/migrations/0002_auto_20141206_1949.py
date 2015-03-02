# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AuthGroup',
        ),
        migrations.DeleteModel(
            name='AuthGroupPermissions',
        ),
        migrations.DeleteModel(
            name='AuthPermission',
        ),
        migrations.DeleteModel(
            name='AuthUser',
        ),
        migrations.DeleteModel(
            name='AuthUserGroups',
        ),
        migrations.DeleteModel(
            name='AuthUserUserPermissions',
        ),
        migrations.DeleteModel(
            name='Comments',
        ),
        migrations.DeleteModel(
            name='DjangoAdminLog',
        ),
        migrations.DeleteModel(
            name='DjangoContentType',
        ),
        migrations.DeleteModel(
            name='DjangoMigrations',
        ),
        migrations.DeleteModel(
            name='DjangoSession',
        ),
        migrations.DeleteModel(
            name='Posts',
        ),
        migrations.DeleteModel(
            name='TaggedPosts',
        ),
        migrations.DeleteModel(
            name='UniqueTags',
        ),
        migrations.DeleteModel(
            name='Users',
        ),
        migrations.DeleteModel(
            name='Votes',
        ),
        migrations.RenameField(
            model_name='resources',
            old_name='description',
            new_name='text',
        ),
        migrations.RenameField(
            model_name='topics',
            old_name='description',
            new_name='text',
        ),
        migrations.RemoveField(
            model_name='resources',
            name='topic',
        ),
        migrations.RemoveField(
            model_name='topicrelations',
            name='from_node',
        ),
        migrations.RemoveField(
            model_name='topicrelations',
            name='to_node',
        ),
        migrations.RemoveField(
            model_name='topics',
            name='children',
        ),
        migrations.RemoveField(
            model_name='topics',
            name='parents',
        ),
        migrations.AddField(
            model_name='topicrelations',
            name='from_resource',
            field=models.ForeignKey(related_name='resources', blank=True, to='sodata.Resources', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='topicrelations',
            name='to_resource',
            field=models.ForeignKey(related_name='parent_topics', blank=True, to='sodata.Resources', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='topics',
            name='child_resources',
            field=models.ManyToManyField(related_name='child_resources_rel_+', to='sodata.Topics'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='topics',
            name='url',
            field=models.URLField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='resources',
            name='url',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='topics',
            name='id',
            field=models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True),
        ),
        migrations.AlterField(
            model_name='topics',
            name='title',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
