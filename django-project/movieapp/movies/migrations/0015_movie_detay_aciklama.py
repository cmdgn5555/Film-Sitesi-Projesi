# Generated by Django 5.0.8 on 2024-08-15 13:08

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0014_alter_movie_aciklama'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='detay_aciklama',
            field=ckeditor.fields.RichTextField(null=True),
        ),
    ]