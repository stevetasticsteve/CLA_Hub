# Generated by Django 3.1.1 on 2020-09-23 07:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='person',
            old_name='dialect',
            new_name='originally_from',
        ),
    ]
