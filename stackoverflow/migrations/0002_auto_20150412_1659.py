# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stackoverflow', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sotaggedposts',
            name='user',
            field=models.ForeignKey(blank=True, to='stackoverflow.SOUsers', null=True),
        ),
    ]
