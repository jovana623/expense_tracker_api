# Generated by Django 5.0.4 on 2024-08-12 16:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0007_transactions_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactions',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
