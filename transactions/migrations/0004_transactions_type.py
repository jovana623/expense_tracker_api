# Generated by Django 5.0.4 on 2024-08-09 15:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0003_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactions',
            name='type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='transactions.types'),
            preserve_default=False,
        ),
    ]
