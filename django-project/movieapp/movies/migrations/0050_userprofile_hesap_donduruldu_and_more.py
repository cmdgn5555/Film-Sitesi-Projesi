# Generated by Django 5.0.8 on 2024-09-17 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0049_remove_userprofile_hesap_donduruldu_and_more'),
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
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
