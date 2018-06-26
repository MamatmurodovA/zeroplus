# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-23 12:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_remove_color_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='colors',
            field=models.ManyToManyField(blank=True, null=True, to='products.Color'),
        ),
    ]