# Generated by Django 4.2.16 on 2025-03-24 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tutor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('experience', models.IntegerField(help_text='Years of experience')),
                ('qualification', models.CharField(max_length=255)),
                ('success_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('image', models.ImageField(default='media/noimage.png', upload_to='tutors/')),
            ],
        ),
    ]
