# Generated by Django 5.0.4 on 2024-08-12 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='last_login',
            field=models.DateField(auto_now_add=True),
        ),
    ]
