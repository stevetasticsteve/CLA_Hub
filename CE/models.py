from django.db import models

class CultureEvent(models.Model):
    title = models.CharField(max_length=60)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    participation = models.TextField(default='no data yet')
    description = models.TextField(default='no data yet')
    differences = models.TextField(default='no data yet')

class Texts(models.Model):
    culture_event = models.ForeignKey('CultureEvent', on_delete=models.PROTECT)
    audio = models.FileField(upload_to='uploads/') #todo add the CE id to this
    phonetic_text = models.TextField(default='no data yet')
    orthographic_text = models.TextField(default='no data yet')


class Pictures(models.Model):
    culture_event = models.ForeignKey('CultureEvent', on_delete=models.CASCADE)
    picture = models.FileField(upload_to='uploads/') #todo add the CE id here
