# Generated by Django 3.0.2 on 2020-02-06 20:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_order_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='quantity',
        ),
    ]
