# Generated by Django 2.0.1 on 2018-03-01 13:34

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('polls', '0002_organismo_antieconomico'),
        ('desconocidos', '0002_auto_20180301_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='actuaciones',
            name='desconocido',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='desconocidos.Desconocido'),
        ),
        migrations.AddField(
            model_name='actuaciones',
            name='revisado',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='actuaciones',
            name='usuario',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='desconocido',
            name='cuota',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='desconocido',
            name='expediente',
            field=models.CharField(blank=True, max_length=14, null=True),
        ),
        migrations.AddField(
            model_name='desconocido',
            name='fk_muni',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='polls.municipio'),
        ),
        migrations.AddField(
            model_name='desconocido',
            name='importe_liq',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name='desconocido',
            name='liq',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='desconocido',
            name='mt',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='desconocido',
            name='nif_candidato',
            field=models.CharField(blank=True, max_length=9, null=True),
        ),
        migrations.AddField(
            model_name='desconocido',
            name='telefono',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='desconocido',
            name='tipo',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.DO_NOTHING, to='desconocidos.tipoDesc'),
        ),
        migrations.AddField(
            model_name='desconocido',
            name='titular_candidato',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='actuaciones',
            name='fecha',
            field=models.DateTimeField(default=datetime.datetime.today),
        ),
        migrations.AlterUniqueTogether(
            name='desconocido',
            unique_together={('fk_muni', 'refcat')},
        ),
    ]
