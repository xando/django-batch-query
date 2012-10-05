from django.db import models
from batch_query import BatchManager

class Section(models.Model):
    name = models.CharField(max_length=32)

class Location(models.Model):
    name = models.CharField(max_length=32)

class Entry(models.Model):
    name = models.CharField(max_length=255)
    section  = models.ForeignKey(Section, blank=True, null=True)
    location = models.ForeignKey(Location, blank=True, null=True)

    objects = BatchManager()
