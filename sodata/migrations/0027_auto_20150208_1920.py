# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sodata', '0026_resources_is_home'),
    ]

    operations = [
        migrations.CreateModel(
            name='TfidfMatrix',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('term', models.TextField()),
                ('tfidf', models.FloatField()),
                ('resource', models.ForeignKey(related_name=b'tfidf_vector', to='sodata.Resources')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='topicrelations',
            name='confidence',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='topicrelations',
            unique_together=set([('to_resource', 'from_resource')]),
        ),
    ]
