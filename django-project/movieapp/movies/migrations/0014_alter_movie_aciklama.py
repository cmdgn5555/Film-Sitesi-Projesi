# Generated by Django 5.0.8 on 2024-08-15 12:08

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0013_movie_oyuncular'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='aciklama',
            field=ckeditor.fields.RichTextField(),
        ),
    ]
