# Generated by Django 2.0.1 on 2018-02-16 08:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('desconocidos', '0009_auto_20180216_0924'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tipodesc',
            options={'verbose_name_plural': 'Tipos de desconocido'},
        ),
        migrations.AlterModelOptions(
            name='usos',
            options={'verbose_name_plural': 'Usos'},
        ),
        migrations.AlterField(
            model_name='desconocido',
            name='tipo',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.DO_NOTHING, to='desconocidos.tipoDesc'),
        ),
    ]