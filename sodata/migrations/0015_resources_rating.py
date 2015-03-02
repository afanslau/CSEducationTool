# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0014_auto_20141209_2123'),
    ]

    operations = [
        migrations.AddField(
            model_name='resources',
            name='rating',
            field=models.IntegerField(default=0, blank=True),
            preserve_default=True,
        ),
    ]
