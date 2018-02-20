# Generated by Django 2.0.1 on 2018-02-15 08:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_organismo'),
    ]

    operations = [
        migrations.CreateModel(
            name='municipio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cod', models.CharField(max_length=5)),
                ('nombre', models.CharField(max_length=100)),
                ('tipo_impositivo', models.DecimalField(decimal_places=3, max_digits=4)),
                ('org', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='polls.organismo')),
            ],
        ),
    ]