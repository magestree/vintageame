# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2019-02-06 12:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0021_auto_20190202_1811'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='producto',
            name='foto_320_320',
        ),
        migrations.RemoveField(
            model_name='producto',
            name='foto_464_299',
        ),
        migrations.RemoveField(
            model_name='producto',
            name='foto_920_614',
        ),
    ]
