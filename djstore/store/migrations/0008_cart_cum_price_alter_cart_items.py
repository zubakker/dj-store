# Generated by Django 4.2.3 on 2023-08-12 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_alter_cart_items'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='cum_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='cart',
            name='items',
            field=models.JSONField(blank=True, default=list),
        ),
    ]