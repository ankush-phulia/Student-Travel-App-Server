# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-05-02 05:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0023_journey_tavel_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='journey',
            old_name='tavel_id',
            new_name='travel_id',
        ),
    ]
