# Generated by Django 5.0.8 on 2024-09-17 17:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0045_remove_userprofile_hesap_donduruldu_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='hesap_donduruldu',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='hesap_dondurulma_bitis_zamani',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 17, 20, 0)),
            preserve_default=False,
        ),
    ]
