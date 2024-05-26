# Generated by Django 5.0.4 on 2024-05-23 04:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buslinesapp', '0020_alter_bill_code_alter_businfor_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businfor',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, unique=True),
        ),
    ]
