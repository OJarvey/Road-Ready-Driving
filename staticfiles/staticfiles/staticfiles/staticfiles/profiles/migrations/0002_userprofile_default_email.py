# Generated by Django 4.2.16 on 2025-03-15 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='default_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
