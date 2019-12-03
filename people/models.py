from django.db import models

class Person(models.Model):
    villages = [
        ('1', 'Elilim'),
        ('2', 'Evesil'),
        ('3', 'Kobumbua'),
        ('4', 'Kokoma'),
        ('5', 'Magilong'),
        ('6', 'Pusilai'),
        ('7', 'Torokum')
    ]
    education_level = [
        ('1', 'None'),
        ('2', 'Grade 1'),
        ('3', 'Grade 2'),
        ('4', 'Grade 4'),
        ('5', 'Grade 10'),
    ]
    picture_folder = 'uploads'

    name = models.CharField(max_length=60, blank=False)
    village = models.CharField(max_length=60, blank=False, choices=villages)
    picture = models.ImageField(upload_to=picture_folder, blank=True)
    clan = models.CharField(max_length=60, blank=True)
    born = models.DateField(auto_now=False)

    medical = models.TextField(blank=True)
    team_contact = models.TextField(blank=True)
    education = models.CharField(max_length=60, blank=False, choices=education_level)

    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.CharField(max_length=20)

    def __str__(self):
        return self.name + '- ' + self.village
