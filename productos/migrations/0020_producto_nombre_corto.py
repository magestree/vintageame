# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2019-02-02 18:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0019_auto_20190202_1808'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='nombre_corto',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Nombre cort'),
        ),
    ]
