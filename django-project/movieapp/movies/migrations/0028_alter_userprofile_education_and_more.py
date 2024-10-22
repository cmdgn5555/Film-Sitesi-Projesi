# Generated by Django 5.0.8 on 2024-09-08 11:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0027_alter_watchlist_unique_together_rating'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='education',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='occupation',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.CreateModel(
            name='Yorum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yorum_text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('film', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='yorumlar', to='movies.movie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]