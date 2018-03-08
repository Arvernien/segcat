# Generated by Django 2.0.1 on 2018-03-08 18:48

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='actuaciones',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(default=datetime.datetime.today)),
                ('descripcion', models.CharField(max_length=400)),
                ('agendar', models.DateField(null=True)),
                ('revisado', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Actuaciones',
            },
        ),
        migrations.CreateModel(
            name='Desconocido',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refcat', models.CharField(blank=True, max_length=20)),
                ('num_fijo', models.CharField(blank=True, max_length=14)),
                ('sigla_via', models.CharField(blank=True, max_length=5)),
                ('nombre_via', models.CharField(blank=True, max_length=100)),
                ('num_pol', models.CharField(blank=True, max_length=4)),
                ('letra_pol', models.CharField(blank=True, max_length=1)),
                ('num_pol_2', models.CharField(blank=True, max_length=4)),
                ('letra_pol_2', models.CharField(blank=True, max_length=1)),
                ('escalera', models.CharField(blank=True, max_length=2)),
                ('planta', models.CharField(blank=True, max_length=3)),
                ('puerta', models.CharField(blank=True, max_length=5)),
                ('dir_no_estruc', models.CharField(blank=True, max_length=25)),
                ('cod_postal', models.CharField(blank=True, max_length=5)),
                ('v_cat', models.IntegerField()),
                ('v_suelo', models.IntegerField()),
                ('v_constru', models.IntegerField()),
                ('b_liquidable', models.IntegerField()),
                ('id_fiscal', models.CharField(blank=True, max_length=10)),
                ('sujeto_pasivo', models.CharField(blank=True, max_length=60)),
                ('resuelto', models.BooleanField(default=False)),
                ('titular_candidato', models.CharField(blank=True, max_length=100, null=True)),
                ('nif_candidato', models.CharField(blank=True, max_length=9, null=True)),
                ('expediente', models.CharField(blank=True, max_length=14, null=True)),
                ('mt', models.BooleanField(default=False)),
                ('liq', models.BooleanField(default=False)),
                ('importe_liq', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, null=True)),
                ('telefono', models.CharField(blank=True, max_length=20, null=True)),
                ('cuota', models.DecimalField(decimal_places=2, max_digits=15, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='tipo_finca',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=15)),
            ],
            options={
                'verbose_name_plural': 'Tipos de finca',
            },
        ),
        migrations.CreateModel(
            name='tipoDesc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name_plural': 'Tipos de desconocido',
            },
        ),
        migrations.CreateModel(
            name='tipotramite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(default='', max_length=20)),
                ('icono', models.CharField(default='', max_length=100)),
            ],
            options={
                'verbose_name_plural': 'Tipos de trámite',
            },
        ),
        migrations.CreateModel(
            name='tramites',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(default=datetime.datetime.today)),
                ('ampliacion', models.TextField(default='')),
                ('agendar', models.DateField(null=True)),
                ('revisado', models.BooleanField(default=False)),
                ('desconocido', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='desconocidos.Desconocido')),
                ('tipo', models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='desconocidos.tipotramite')),
                ('usuario', models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Trámites',
            },
        ),
        migrations.CreateModel(
            name='usos',
            fields=[
                ('clave', models.CharField(max_length=25, primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=25)),
            ],
            options={
                'verbose_name_plural': 'Usos',
            },
        ),
        migrations.AddField(
            model_name='desconocido',
            name='clave_uso',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.DO_NOTHING, to='desconocidos.usos'),
        ),
    ]
