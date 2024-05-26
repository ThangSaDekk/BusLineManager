# Generated by Django 5.0.4 on 2024-05-22 06:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buslinesapp', '0018_alter_ticket_bill_alter_ticket_customer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='seat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='buslinesapp.seat', unique=True),
        ),
    ]
