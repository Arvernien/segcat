# Generated by Django 2.0.1 on 2018-02-15 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0008_auto_20180215_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='municipio',
            name='tipo_impositivo',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=4),
        ),
    ]