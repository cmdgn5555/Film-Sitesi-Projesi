# Generated by Django 5.0.8 on 2024-09-11 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0032_remove_yorum_sikayet_sebebi'),
    ]

    operations = [
        migrations.AddField(
            model_name='yorum',
            name='sikayet_sayisi',
            field=models.PositiveIntegerField(default=0),
        ),
    ]