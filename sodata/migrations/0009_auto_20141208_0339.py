# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import sodata.AutoUpdateDateTimeField


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0008_auto_20141207_0452'),
    ]

    operations = [
        migrations.AddField(
            model_name='resources',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime.now),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resources',
            name='updated_at',
            field=sodata.AutoUpdateDateTimeField.AutoUpdateDateTimeField(default=datetime.datetime.now),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='topicrelations',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime.now),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='topicrelations',
            name='updated_at',
            field=sodata.AutoUpdateDateTimeField.AutoUpdateDateTimeField(default=datetime.datetime.now),
            preserve_default=True,
        ),
    ]
