# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2019-02-02 18:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0020_producto_nombre_corto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='nombre_corto',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Nombre cort'),
        ),
    ]