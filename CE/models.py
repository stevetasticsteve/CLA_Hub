from django.db import models

class CultureEvent(models.Model):
    title = models.CharField(max_length=60, blank=False, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    participation = models.TextField(blank=True)
    description = models.TextField(blank=True)
    differences = models.TextField(blank=True)

    def __str__(self):
        return str(self.title)

class Texts(models.Model):
    ce_id = models.ForeignKey('CultureEvent', on_delete=models.PROTECT)
    audio = models.FileField(upload_to='uploads/') #todo add the CE id to this
    phonetic_text = models.TextField(blank=True)
    orthographic_text = models.TextField(blank=True)

    def __str__(self):
        return 'Text for ' + str(self.ce_id)


class Pictures(models.Model):
    ce_id = models.ForeignKey('CultureEvent', on_delete=models.CASCADE)
    picture = models.FileField(upload_to='uploads/') #todo add the CE id here

    def __str__(self):
        return 'Pictures for ' + str(self.ce_id)

