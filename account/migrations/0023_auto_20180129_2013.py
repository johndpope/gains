# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-01-29 14:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0022_auto_20180129_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trading_platform',
            name='trading_platform',
            field=models.CharField(choices=[(b'Quadrigacx', b'Quadrigacx'), (b'Kraken', b'Kraken'), (b'Bitfinex', b'Bitfinex'), (b'Quoine', b'Quoine')], default=None, max_length=100),
        ),
    ]