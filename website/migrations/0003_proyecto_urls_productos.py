# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2019-01-01 18:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_proyecto_en_uso'),
    ]

    operations = [
        migrations.AddField(
            model_name='proyecto',
            name='urls_productos',
            field=models.TextField(blank=True, null=True, verbose_name='URLs de Productos'),
        ),
    ]