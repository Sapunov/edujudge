# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-13 20:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20170413_1711'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='solution',
            name='is_error',
        ),
        migrations.AddField(
            model_name='solution',
            name='error',
            field=models.SmallIntegerField(default=0),
        ),
    ]