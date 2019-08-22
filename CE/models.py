from django.db import models
from django.utils.text import slugify
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from io import BytesIO

import CE.settings
import sys
import re

class CultureEvent(models.Model):
    title = models.CharField(max_length=60, blank=False, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.CharField(max_length=20)
    # plain text description is what the user has entered. description is a processed version of the plain text
    # that adds hyperlinks and is displayed escaped so the html generates
    description = models.TextField(blank=True)
    description_plain_text = models.TextField(blank=True)

    differences = models.TextField(blank=True)
    interpretation = models.TextField(blank=True)
    slug = models.SlugField(unique=True) # set in save function, form doesn't need to validate it

    def save(self):
        # copy the user's input from plain text to description to be processed
        self.description = self.description_plain_text
        if CE.settings.auto_cross_reference:
            self.auto_cross_ref()
        else:
            self.find_tag()
        self.slug = slugify(self.title)
        super().save()

    def find_tag(self):
        # todo case sensitive, shouldn't be
        # find anything in the plain text description with {} around it and replace it with a hyperlink if valid
        # only triggers if auto_cross_reference is False
        tags = re.findall(r'{.+?}', self.description)
        ce_slugs = self.list_slugs()
        for tag in tags:
            content = tag
            content = content.strip('{')
            content = content.strip('}')
            for i, title_slug in enumerate(ce_slugs):
                # if slug found within {} replace with hyperlink
                if title_slug in slugify(content):
                    title_deslug = title_slug.replace('-', ' ')
                    slug_href = '<a href="' + title_slug + '">' + title_deslug + '</a>'
                    self.description = self.description.replace('{'+ title_deslug + '}', slug_href)
                # if none of the title slugs are found remove the {}
                elif i == len(ce_slugs) - 1:
                    self.description = self.description.replace(tag, content)


    def auto_cross_ref(self):
        # todo Will miss cases where user uses a capital. Currently only works with lower case.
        # search the plain text description for slugs and replace them with hyperlinks if found
        # only triggers if auto_cross_reference is True
        slugged_description = slugify(self.description_plain_text)
        ce_slugs = self.list_slugs()
        for title_slug in ce_slugs:
            if title_slug in slugged_description:
                title_deslug = title_slug.replace('-', ' ')
                slug_href = '<a href="' + title_slug + '">' + title_deslug + '</a>'
                self.description = self.description.replace(title_deslug, slug_href)

    def list_slugs(self):
        ce_objects = CultureEvent.objects.all()
        ce_slugs = [i.slug for i in ce_objects]
        return ce_slugs

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
    phonetic_standard = models.CharField(choices=[('1', 'Unchecked'),
                                                  ('2', 'Double checked by author'),
                                                  ('3', 'Checked by team mate'),
                                                  ('4', 'Approved by whole team'),
                                                  ('5', 'Valid for linguistic analysis')],
                                         max_length=30,
                                         blank=True)
    orthographic_text = models.TextField(blank=True)
    valid_for_DA = models.BooleanField()
    discourse_type = models.CharField(choices=[('1', 'Narrative'),
                                               ('2', 'Hortatory'),
                                               ('3', 'Procedural'),
                                               ('4', 'Expository'),
                                               ('5', 'Descriptive')],
                                      max_length=15,
                                      blank=True)

    def __str__(self):
        return 'Text for ' + str(self.ce)



