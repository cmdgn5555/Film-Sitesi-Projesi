# Generated by Django 5.0.8 on 2024-08-24 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0018_movie_goruntulenme_sayisi_alter_movie_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='vizyon_tarihi',
            field=models.DateField(blank=True, null=True),
        ),
    ]
