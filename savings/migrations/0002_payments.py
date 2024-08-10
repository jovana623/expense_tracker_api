# Generated by Django 5.0.4 on 2024-08-09 16:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('savings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateField(auto_now_add=True)),
                ('saving', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='savings.savings')),
            ],
        ),
    ]
