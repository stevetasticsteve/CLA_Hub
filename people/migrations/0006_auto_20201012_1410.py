# Generated by Django 3.1.1 on 2020-10-12 04:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0005_auto_20201012_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicalassessment',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
