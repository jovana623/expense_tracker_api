# Generated by Django 5.0.4 on 2024-08-13 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('savings', '0004_alter_payments_date_alter_savings_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='savings',
            name='status',
            field=models.CharField(choices=[('In progress', 'In Progress'), ('Completed', 'Completed'), ('On hold', 'On Hold')], max_length=50),
        ),
    ]