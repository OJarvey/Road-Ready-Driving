from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0008_order_user_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderlineitem',
            name='package',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.SET_NULL,
                related_name='lineitems',
                to='packages.package'
            ),
        ),
    ]