# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2019-02-09 21:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='email',
            field=models.EmailField(max_length=128, verbose_name='Email'),
        ),
    ]
