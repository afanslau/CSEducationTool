# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0022_auto_20150107_0053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrelation',
            name='resource',
            field=models.ForeignKey(related_name=b'user_relations', to='sodata.Resources'),
        ),
        migrations.AlterField(
            model_name='userrelation',
            name='user',
            field=models.ForeignKey(related_name=b'user_relations', to=settings.AUTH_USER_MODEL),
        ),
    ]
