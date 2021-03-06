# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2019-07-16 01:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20190710_1622'),
    ]

    operations = [
        migrations.AddField(
            model_name='townie',
            name='state',
            field=models.CharField(choices=[('3_rejected', 'Rejected'), ('2_accepted', 'Accepted'), ('0_unreviewed', 'Unreviewed'), ('4_permaban', 'Permanently Banned'), ('1_tempban', 'Temporarily Banned')], default='0_unreviewed', max_length=20),
        ),
        migrations.AlterField(
            model_name='townie',
            name='notes',
            field=models.TextField(blank=True, help_text='Use this field to share information about this user (reviewed or not) for other admins to see', null=True),
        ),
    ]
