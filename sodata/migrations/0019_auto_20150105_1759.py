# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0018_auto_20150103_1844'),
    ]

    operations = [
        migrations.AddField(
            model_name='resources',
            name='full_page_cache',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resources',
            name='html_text',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resources',
            name='last_cache_time',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
