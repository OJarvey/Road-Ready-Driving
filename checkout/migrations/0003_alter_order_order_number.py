# Generated by Django 4.2.16 on 2025-02-24 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0002_order_order_number_alter_order_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_number',
            field=models.CharField(default='TEMP-ORDER-NUMBER', editable=False, max_length=32, unique=True),
            preserve_default=False,
        ),
    ]
