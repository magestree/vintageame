# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2019-01-01 18:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_proyecto_urls_productos'),
        ('productos', '0016_categoria_proyecto'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='categoria',
            name='proyecto',
        ),
        migrations.AddField(
            model_name='producto',
            name='proyecto',
            field=models.ForeignKey(blank='True', null=True, on_delete=django.db.models.deletion.CASCADE, to='website.Proyecto'),
        ),
    ]