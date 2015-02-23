# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0028_auto_20150208_2235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topicrelations',
            name='confidence',
            field=models.FloatField(default=0.5),
        ),
        migrations.AlterUniqueTogether(
            name='topicrelations',
            unique_together=None,
        ),
    ]
