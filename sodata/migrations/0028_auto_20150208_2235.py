# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0027_auto_20150208_1920'),
    ]

    operations = [
        migrations.AddField(
            model_name='tfidfmatrix',
            name='col',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tfidfmatrix',
            name='row',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
