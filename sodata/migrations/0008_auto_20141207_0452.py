# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0007_auto_20141206_2313'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='topics',
            name='child_resources',
        ),
        migrations.DeleteModel(
            name='Topics',
        ),
    ]
