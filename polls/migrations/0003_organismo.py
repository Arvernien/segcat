# Generated by Django 2.0.1 on 2018-02-03 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_finca'),
    ]

    operations = [
        migrations.CreateModel(
            name='organismo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cod', models.CharField(max_length=5)),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
    ]