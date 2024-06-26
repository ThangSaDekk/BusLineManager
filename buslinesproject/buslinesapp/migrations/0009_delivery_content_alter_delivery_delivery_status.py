# Generated by Django 5.0.4 on 2024-05-03 04:46

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buslinesapp', '0008_bill_seat_status_delivery_ticket'),
    ]

    operations = [
        migrations.AddField(
            model_name='delivery',
            name='content',
            field=ckeditor.fields.RichTextField(null=True),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='delivery_status',
            field=models.BooleanField(default=False),
        ),
    ]
