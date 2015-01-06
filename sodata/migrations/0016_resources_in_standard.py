# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0015_resources_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='resources',
            name='in_standard',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
