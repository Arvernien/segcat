# Generated by Django 2.0.1 on 2018-02-15 16:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('polls', '0007_auto_20180215_1653'),
        ('desconocidos', '0002_delete_testeo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Desconocido',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refcat', models.CharField(max_length=20)),
                ('num_fijo', models.CharField(max_length=14)),
                ('sigla_via', models.CharField(max_length=5)),
                ('nombre_via', models.CharField(max_length=100)),
                ('num_pol', models.CharField(max_length=4)),
                ('letra_pol', models.CharField(max_length=1)),
                ('num_pol_2', models.CharField(max_length=4)),
                ('letra_pol_2', models.CharField(max_length=1)),
                ('escalera', models.CharField(max_length=2)),
                ('planta', models.CharField(max_length=3)),
                ('puerta', models.CharField(max_length=5)),
                ('dir_no_estruc', models.CharField(max_length=25)),
                ('cod_postal', models.CharField(max_length=5)),
                ('v_cat', models.IntegerField()),
                ('v_suelo', models.IntegerField()),
                ('v_constru', models.IntegerField()),
                ('b_liquidable', models.IntegerField()),
                ('clave_uso', models.CharField(max_length=25)),
                ('id_fiscal', models.CharField(max_length=10)),
                ('sujeto_pasivo', models.CharField(max_length=60)),
                ('fk_muni', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='polls.municipio')),
            ],
        ),
    ]