# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0009_auto_20141208_0339'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resources',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='resources',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='topicrelations',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='topicrelations',
            name='updated_at',
        ),
    ]
