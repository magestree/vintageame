# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2019-01-22 18:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0018_remove_producto_proyecto'),
        ('website', '0006_mejor_valorado'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='descuento',
            name='proyecto',
        ),
        migrations.RemoveField(
            model_name='mejor_valorado',
            name='proyecto',
        ),
        migrations.DeleteModel(
            name='Descuento',
        ),
        migrations.DeleteModel(
            name='Mejor_Valorado',
        ),
        migrations.DeleteModel(
            name='Proyecto',
        ),
    ]
