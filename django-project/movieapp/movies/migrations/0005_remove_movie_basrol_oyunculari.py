# Generated by Django 5.0.8 on 2024-08-11 18:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0004_movie_basrol_oyunculari_alter_movie_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movie',
            name='basrol_oyunculari',
        ),
    ]
