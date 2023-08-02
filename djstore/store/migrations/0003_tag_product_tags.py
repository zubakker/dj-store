# Generated by Django 4.2.3 on 2023-08-02 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_product_author'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=31)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(to='store.tag'),
        ),
    ]
