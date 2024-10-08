# Generated by Django 5.0.4 on 2024-08-09 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Savings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('goal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('target_date', models.DateField()),
                ('status', models.CharField(max_length=50)),
                ('color', models.CharField(max_length=7)),
                ('description', models.TextField()),
            ],
        ),
    ]
