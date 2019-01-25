# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2019-01-19 18:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20170114_0757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pubkey',
            name='key_type',
            field=models.CharField(choices=[('ssh-rsa', 'ssh-rsa'), ('ssh-dss', 'ssh-dss'), ('ecdsa-sha2-nistp256', 'ecdsa-sha2-nistp256')], max_length=50),
        ),
    ]
