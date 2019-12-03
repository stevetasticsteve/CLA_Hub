from django.db import models
from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image
from io import BytesIO

import sys

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
    picture_folder = 'people/profile_pictures'
    thumbnail_folder = 'people/thumbnails'

    name = models.CharField(max_length=60, blank=False)
    village = models.CharField(max_length=60, blank=False, choices=villages)
    picture = models.ImageField(upload_to=picture_folder, blank=True)
    clan = models.CharField(max_length=60, blank=True)
    born = models.DateField(auto_now=False, blank=True, null=True)

    medical = models.TextField(blank=True)
    team_contact = models.TextField(blank=True)
    education = models.CharField(max_length=60, blank=True, choices=education_level)

    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.CharField(max_length=20)
    thumbnail = models.ImageField(upload_to=thumbnail_folder, blank=True)

    def save(self):
        '''Custom save method that compresses pictures so they are under 500kb'''
        if self.picture:
            size = 1200, 1200
            thumb = Image.open(self.picture)
            thumb = thumb.copy()
            output = BytesIO()
            thumb.thumbnail(size)
            thumb.save(output, format='JPEG', quality=90)
            output.seek(0)
            # args = (file, string type repr, name of file, charset, size)
            self.picture = InMemoryUploadedFile(output, 'PictureField',
                                                "%s.jpg" % self.picture.name.split('.')[0],
                                                'filename',
                                                'image/jpeg',
                                                 sys.getsizeof(output), None)
            # save an even smaller thumbnail
            thumbnail_size = 300, 300
            output = BytesIO()
            thumb.thumbnail(thumbnail_size)
            thumb.save(output, format='JPEG', quality=90)
            output.seek(0)
            self.thumbnail = InMemoryUploadedFile(output, 'ThumbnailField',
                                                "%s_thumbnail.jpg" % self.picture.name.split('.')[0],
                                                'image/jpeg',
                                                sys.getsizeof(output), None)

        super(Person, self).save()

    def __str__(self):
        return self.name + '- ' + self.village
