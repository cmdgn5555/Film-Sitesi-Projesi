# Generated by Django 5.0.8 on 2024-09-11 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0030_yorum_sikayet_edenler'),
    ]

    operations = [
        migrations.AddField(
            model_name='yorum',
            name='sikayet_sebebi',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
