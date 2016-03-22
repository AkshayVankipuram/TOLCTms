# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-21 23:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('TMS', '0004_auto_20160321_2155'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grouptask',
            name='task',
        ),
        migrations.AddField(
            model_name='tmsgroup',
            name='completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tmsgroup',
            name='evaluated',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='tmsgroup',
            name='task',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='TMS.Task'),
        ),
        migrations.DeleteModel(
            name='GroupTask',
        ),
    ]
