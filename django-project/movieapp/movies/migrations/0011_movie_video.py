# Generated by Django 5.0.8 on 2024-08-13 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0010_remove_movie_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='videos'),
        ),
    ]
