# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-21 06:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20160617_2254'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='subscription_enddate',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='myuser',
            name='subscription_startdate',
            field=models.DateTimeField(null=True),
        ),
    ]
