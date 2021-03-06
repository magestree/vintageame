# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-11-25 17:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0006_auto_20181125_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoria',
            name='descripcion',
            field=models.TextField(blank=True, max_length=4096, null=True, verbose_name='Descripción'),
        ),
        migrations.AlterField(
            model_name='categoria',
            name='nombre',
            field=models.TextField(max_length=4096, verbose_name='Categoría'),
        ),
        migrations.AlterField(
            model_name='sub_categoria',
            name='descripcion',
            field=models.TextField(blank=True, max_length=4096, null=True, verbose_name='Descripción'),
        ),
        migrations.AlterField(
            model_name='sub_categoria',
            name='nombre',
            field=models.TextField(max_length=4096, verbose_name='Sub Categoría'),
        ),
    ]
