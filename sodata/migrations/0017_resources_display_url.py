# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0016_resources_in_standard'),
    ]

    operations = [
        migrations.AddField(
            model_name='resources',
            name='display_url',
            field=models.URLField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
