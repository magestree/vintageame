# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-12-27 11:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0014_producto_fecha_registro'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sub_categoria',
            name='categoria',
        ),
        migrations.RemoveField(
            model_name='producto',
            name='sub_categoria',
        ),
        migrations.DeleteModel(
            name='Sub_Categoria',
        ),
    ]
