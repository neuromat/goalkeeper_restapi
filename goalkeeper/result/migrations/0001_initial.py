# Generated by Django 2.2 on 2019-05-29 17:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('game', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GameResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('move', models.IntegerField()),
                ('waited_result', models.IntegerField()),
                ('is_random', models.BooleanField()),
                ('option_chosen', models.IntegerField()),
                ('correct', models.BooleanField()),
                ('movement_time', models.FloatField()),
                ('pause_time', models.FloatField()),
                ('time_running', models.FloatField()),
                ('game_phase', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='game.Game')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='game_results', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
