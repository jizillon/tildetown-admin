# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2019-07-10 16:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20190416_0126'),
    ]

    operations = [
        migrations.AddField(
            model_name='townie',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='townie',
            name='referral',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
