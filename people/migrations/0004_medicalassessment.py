# Generated by Django 3.1.1 on 2020-09-25 09:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0003_person_gender'),
    ]

    operations = [
        migrations.CreateModel(
            name='MedicalAssessment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subjective', models.TextField()),
                ('objective', models.TextField()),
                ('assessment', models.TextField()),
                ('plan', models.TextField()),
                ('date', models.DateField(auto_now_add=True)),
                ('short', models.CharField(max_length=25)),
                ('image', models.ImageField(blank=True, upload_to='people/medical')),
                ('comment', models.TextField(blank=True)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.person')),
            ],
        ),
    ]
