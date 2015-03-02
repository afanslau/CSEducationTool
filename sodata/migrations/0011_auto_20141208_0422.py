# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0010_auto_20141208_0400'),
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
            field=models.DateTimeField(default=datetime.datetime.now),
            preserve_default=True,
        ),
    ]
