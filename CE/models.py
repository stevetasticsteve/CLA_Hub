from django.db import models
from django.utils.text import slugify
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from io import BytesIO

import sys
import re

class CultureEvent(models.Model):
    title = models.CharField(max_length=60, blank=False, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    differences = models.TextField(blank=True)
    slug = models.SlugField(unique=True) # set in save function, form doesn't need to validate it

    def save(self):
        self.find_regexs(self.description)
        self.slug = slugify(self.title)
        super().save()

    def find_regexs(self, target):
        tags = re.findall(r'{.+?}', target)
        for tag in tags:
            content = tag
            content = content.strip('{')
            content = content.strip('}')
            self.description= self.description.replace(tag, '<strong>' + content + '</strong>')

    def __str__(self):
        return str(self.title)


class ParticipationModel(models.Model):
    ce = models.ForeignKey('CultureEvent', on_delete=models.CASCADE)
    team_participants = models.CharField(blank=True, max_length=60)
    national_participants = models.CharField(blank=True, max_length=60)
    date = models.DateField(blank=False)

    def __str__(self):
        return str('Participants for ' + str(self.ce))


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


class TextModel(models.Model):
    ce = models.ForeignKey('CultureEvent', on_delete=models.PROTECT)
    audio = models.FileField(upload_to=audio_folder, blank=False)
    phonetic_text = models.TextField(blank=True)
    phonetic_standard = models.CharField(choices=[('1', 'Unchecked' ),
                                                  ('2', 'Double checked by author'),
                                                  ('3', 'Checked by team mate'),
                                                  ('4', 'Approved by whole team'),
                                                  ('5', 'Valid for linguistic analysis')],
                                         max_length=30,
                                         blank=True)
    orthographic_text = models.TextField(blank=True)

    def __str__(self):
        return 'Text for ' + str(self.ce)



