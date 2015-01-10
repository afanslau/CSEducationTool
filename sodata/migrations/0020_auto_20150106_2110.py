# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sodata', '0019_auto_20150105_1759'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activity_type', models.IntegerField(default=3, choices=[(0, b'Starred'), (3, b'Created'), (4, b'Edited'), (5, b'Visited'), (2, b'Not a relevant resource to its parent'), (1, b'Add ')])),
                ('resource', models.ForeignKey(to='sodata.Resources')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_type', models.IntegerField(default=0, choices=[(0, b'Viewer'), (1, b'Author')])),
                ('starred', models.BooleanField(default=False)),
                ('num_visits', models.IntegerField(default=0)),
                ('last_visited', models.DateTimeField(default=django.utils.timezone.now)),
                ('resource', models.ForeignKey(to='sodata.Resources')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='resources',
            name='author',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
