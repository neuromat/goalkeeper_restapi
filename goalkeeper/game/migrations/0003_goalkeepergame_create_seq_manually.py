# Generated by Django 2.2 on 2019-06-25 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_auto_20190625_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='goalkeepergame',
            name='create_seq_manually',
            field=models.CharField(choices=[('no', 'No'), ('yes', 'Yes')], default='no', max_length=3),
        ),
    ]