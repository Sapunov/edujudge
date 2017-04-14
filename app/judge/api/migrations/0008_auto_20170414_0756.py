# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-14 07:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_solution_testnum'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solution',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solutions', to='api.Task'),
        ),
    ]