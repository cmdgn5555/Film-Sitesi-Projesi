# Generated by Django 5.0.8 on 2024-09-16 19:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0038_userprofile_dondurulma_bitis_tarihi_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='dondurulma_bitis_tarihi',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='hesap_donduruldu',
        ),
    ]