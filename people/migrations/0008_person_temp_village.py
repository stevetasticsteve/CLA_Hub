# Generated by Django 3.1.6 on 2021-02-19 10:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0007_auto_20210219_2023'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='temp_village',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='people.village'),
        ),
    ]
