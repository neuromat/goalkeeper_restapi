# Generated by Django 2.2 on 2019-06-26 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_goalkeepergame_create_seq_manually'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='number_of_plays',
            field=models.IntegerField(),
        ),
    ]
