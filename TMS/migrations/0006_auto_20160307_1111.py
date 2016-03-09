# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-07 18:11
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TMS', '0005_auto_20160307_1103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='skill_1_lvl',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='task',
            name='skill_2_lvl',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='task',
            name='skill_3_lvl',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='task',
            name='skill_4_lvl',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
    ]
