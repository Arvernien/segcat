# Generated by Django 2.0.1 on 2018-03-08 18:48

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice_text', models.CharField(max_length=200)),
                ('votes', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Finca',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refcat', models.CharField(max_length=14)),
                ('TipoFinca', models.CharField(choices=[('PROPIA', 'PROPIA'), ('AFECTADA', 'AFECTADA'), ('GRÁFICO', 'GRÁFICO')], default='PROPIA', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='municipio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cod', models.IntegerField()),
                ('nombre', models.CharField(max_length=100)),
                ('tipo_impositivo', models.DecimalField(blank=True, decimal_places=4, max_digits=5, null=True)),
                ('tipo_impositivo_ru', models.DecimalField(blank=True, decimal_places=4, max_digits=5, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='organismo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cod', models.IntegerField(validators=[django.core.validators.MaxValueValidator(99)])),
                ('nombre', models.CharField(max_length=100)),
                ('antieconomico', models.DecimalField(decimal_places=2, max_digits=4)),
                ('grupo', models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='auth.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=200)),
                ('pub_date', models.DateTimeField(verbose_name='fecha de publicación')),
            ],
        ),
        migrations.AddField(
            model_name='municipio',
            name='org',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='polls.organismo'),
        ),
        migrations.AddField(
            model_name='choice',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.Question'),
        ),
        migrations.AlterUniqueTogether(
            name='municipio',
            unique_together={('org', 'cod')},
        ),
    ]
