# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0023_auto_20150107_0055'),
    ]

    operations = [
        migrations.AddField(
            model_name='useractivity',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='useractivity',
            name='activity_type',
            field=models.IntegerField(default=3, choices=[(0, b'Starred'), (3, b'Created'), (4, b'Edited'), (5, b'Visited'), (2, b'Not a relevant resource to its parent'), (1, b'Added to a topic'), (6, b'Reported as spam')]),
        ),
        migrations.AlterField(
            model_name='useractivity',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
