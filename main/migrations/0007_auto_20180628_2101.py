# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-28 16:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_bannertranslation_body'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bannertranslation',
            name='slug',
        ),
        migrations.AddField(
            model_name='bannertranslation',
            name='url',
            field=models.CharField(max_length=60, null=True, verbose_name='Url'),
        ),
    ]
