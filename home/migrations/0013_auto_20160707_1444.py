# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-07-07 09:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_contact_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]