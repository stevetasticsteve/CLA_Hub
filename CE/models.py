from django.db import models
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from io import BytesIO

import sys

class CultureEvent(models.Model):
    title = models.CharField(max_length=60, blank=False, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.CharField(max_length=20)
    participation = models.TextField(blank=True) #todo change to a many to one
    description = models.TextField(blank=True)
    differences = models.TextField(blank=True)

    def __str__(self):
        return str(self.title)


# provide file folders to save audio and pictures in using foreign keys
def picture_folder(instance, filename):
    return '/'.join(['CultureEventFiles', str(instance.ce.id), 'images', filename])


def audio_folder(instance, filename):
    return '/'.join(['CultureEventFiles', str(instance.ce.id), 'audio', filename])


class PictureModel(models.Model):
    ce = models.ForeignKey('CultureEvent', on_delete=models.CASCADE)
    picture = models.ImageField(upload_to=picture_folder, blank=True)
    # blank=True is a fudge. Trying to display multiple models in a single form and it wont'
    # submit if there is validation. The view function makes sure blank entries aren't saved though

    def __str__(self):
        return 'Picture for ' + str(self.ce)

    def save(self):
        im = Image.open(self.picture)
        output = BytesIO()
        im = im.resize((1200, 900))
        im.save(output, format='JPEG', quality=90)
        output.seek(0)
        self.picture = InMemoryUploadedFile(output, 'PictureField',
                                            "%s.jpg" % self.picture.name.split('.')[0],
                                            'image/jpeg',
                                             sys.getsizeof(output), None)

        super(PictureModel, self).save()


class Texts(models.Model):
    ce = models.ForeignKey('CultureEvent', on_delete=models.PROTECT)
    audio = models.FileField(upload_to=audio_folder)
    phonetic_text = models.TextField(blank=True)
    orthographic_text = models.TextField(blank=True)

    def __str__(self):
        return 'Text for ' + str(self.ce)

