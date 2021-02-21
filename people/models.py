import re

import bleach
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.timezone import now

from CLAHub import tools

integer_regex = re.compile(' \d+')


class Village(models.Model):
    village_name = models.CharField(max_length=15, blank=False)

    def __str__(self):
        return self.village_name


class Person(models.Model):
    def __init__(self, *args, **kwargs):
        super(Person, self).__init__(*args, **kwargs)
        self.original_picture = self.picture

    education_level = [
        ('1', 'None'),
        ('2', 'Grade 1'),
        ('3', 'Grade 2'),
        ('4', 'Grade 4'),
        ('5', 'Grade 10'),
    ]
    picture_folder = 'people/profile_pictures'
    thumbnail_folder = 'people/thumbnails'

    name = models.CharField(max_length=60, blank=False)

    village = models.ForeignKey(Village, blank=False, null=True, on_delete=models.SET_NULL)
    picture = models.ImageField(upload_to=picture_folder, blank=True)
    clan = models.CharField(max_length=60, blank=True)
    born = models.DateField(auto_now=False, blank=True, null=True)
    originally_from = models.CharField(max_length=60, blank=True)
    death = models.DateField(auto_now=False, blank=True, null=True)
    family_plain_text = models.TextField(blank=True)
    family = models.TextField(blank=True)
    gender = models.CharField(max_length=1, blank=True, choices=([('M', 'Male'), ('F', 'Female')]))

    medical = models.TextField(blank=True)
    team_contact = models.TextField(blank=True)
    education = models.CharField(max_length=60, blank=True, choices=education_level)

    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.CharField(max_length=20)
    thumbnail = models.ImageField(upload_to=thumbnail_folder, blank=True)

    def save(self):
        # don't re-upload the same image
        if self.picture:
            if tools.check_already_imported(self.picture):
                self.picture = self.original_picture
            else:
                thumbnail = self.picture  # do this if changing picture
                self.picture = tools.compress_picture(self.picture, (1200, 1200))
                # save an even smaller thumbnail
                self.thumbnail = tools.compress_picture(thumbnail, (300, 300))

        # search the family field for integers that indicate the user intends to add a hyperlink
        if self.family_plain_text:
            integers = re.findall(integer_regex, self.family_plain_text)
            integers.sort(reverse=True)  # start with the biggest number so 5 doesn't replace a single 5 in 55

            self.family = bleach.clean(self.family_plain_text)
            for match in integers:
                try:
                    name = Person.objects.get(pk=match.lstrip()).name
                    # replace ' ##' with a hyperlink. Using lstrip() to remove the space precents being matched twice
                    self.family = self.family.replace(match, '<a href="{i}"> {display}</a>'.format(i=match.lstrip(),
                                                                                                   display=name))
                except ObjectDoesNotExist:
                    pass

        super(Person, self).save()

    def clear_picture(self):
        self.picture = None
        self.thumbnail = None
        self.save()

    def __str__(self):
        return self.name + ' from ' + str(self.village)


class MedicalAssessment(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    subjective = models.TextField(blank=False)
    objective = models.TextField(blank=False)
    assessment = models.TextField(blank=False)
    plan = models.TextField(blank=False)
    date = models.DateField(default=now)
    short = models.CharField(max_length=25, blank=False)
    image = models.ImageField(upload_to='people/medical', blank=True)
    comment = models.TextField(blank=True)

    def __str__(self):
        return str(self.date) + ': ' + self.person.name

    def save(self):
        # Compress picture
        if self.image:
            self.image = tools.compress_picture(self.image, (1000, 1000))
        super(MedicalAssessment, self).save()
