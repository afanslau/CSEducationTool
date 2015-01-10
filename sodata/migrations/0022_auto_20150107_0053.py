# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0021_auto_20150106_2248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrelation',
            name='resource',
            field=models.ForeignKey(to='sodata.Resources'),
        ),
        migrations.AlterField(
            model_name='userrelation',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
