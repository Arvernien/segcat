# Generated by Django 2.0.1 on 2018-02-16 08:24

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0010_auto_20180215_1756'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organismo',
            name='cod',
            field=models.IntegerField(validators=[django.core.validators.MaxValueValidator(99)]),
        ),
    ]
