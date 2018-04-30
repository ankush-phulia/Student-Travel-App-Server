# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-04-30 00:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0011_notification_resolved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journeypoint',
            name='journey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checkpoints', to='info.Journey'),
        ),
    ]
