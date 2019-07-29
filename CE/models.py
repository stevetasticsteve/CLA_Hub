from django.db import models

class CE(models.Model):
    title = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    participation = models.TextField()
    description = models.TextField()
    differences = models.TextField()

class Texts(models.Model):
    ce = models.ForeignKey('CE', on_delete=models.PROTECT)
    audio = models.FileField(upload_to='uploads/') #todo add the CE id to this
    phonetic_text = models.TextField()
    orthographic_text = models.TextField()
