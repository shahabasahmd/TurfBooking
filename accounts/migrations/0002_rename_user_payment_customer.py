# Generated by Django 4.2.2 on 2023-08-02 09:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='user',
            new_name='customer',
        ),
    ]
