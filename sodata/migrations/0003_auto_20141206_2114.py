# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0002_auto_20141206_1949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topics',
            name='id',
            field=models.AutoField(serialize=False, primary_key=True),
        ),
    ]
