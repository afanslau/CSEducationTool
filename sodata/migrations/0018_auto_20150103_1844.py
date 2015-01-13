# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0017_resources_display_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='resources',
            name='bing_id',
            field=models.CharField(max_length=100, unique=True, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resources',
            name='human_created',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
