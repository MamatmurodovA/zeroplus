# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-24 13:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20180624_1833'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='static',
            name='created_at',
        ),
    ]
