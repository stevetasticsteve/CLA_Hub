from django.db import models

class CE(models.Model):
    title = models.CharField(100)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    participation = models.TextField()
