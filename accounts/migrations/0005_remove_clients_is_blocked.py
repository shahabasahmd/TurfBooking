# Generated by Django 4.2.2 on 2023-07-30 04:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_rename_client_clients_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clients',
            name='is_blocked',
        ),
    ]
