# Generated by Django 5.0.8 on 2024-09-11 14:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0031_yorum_sikayet_sebebi'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='yorum',
            name='sikayet_sebebi',
        ),
    ]
