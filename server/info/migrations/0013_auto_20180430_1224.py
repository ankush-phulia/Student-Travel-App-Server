# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-04-30 12:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0012_auto_20180430_0020'),
    ]

    operations = [
        migrations.RenameField(
            model_name='journey',
            old_name='completed',
            new_name='closed',
        ),
    ]
