# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-13 21:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_townie_reasons'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='townie',
            options={'verbose_name': 'Townie', 'verbose_name_plural': 'Townies'},
        ),
        migrations.RemoveField(
            model_name='townie',
            name='pubkey_type',
        ),
    ]
