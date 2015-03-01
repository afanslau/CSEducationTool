# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0025_topicrelations_perspective_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='resources',
            name='is_home',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
