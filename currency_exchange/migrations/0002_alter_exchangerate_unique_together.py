# Generated by Django 5.1.3 on 2024-11-20 21:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('currency_exchange', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='exchangerate',
            unique_together={('currency_from', 'currency_to', 'date')},
        ),
    ]
