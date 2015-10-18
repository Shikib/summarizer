from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    def __str__(self):
        return self.user.username

class Topic(models.Model):
    title = models.CharField(max_length=200)
    subscribers = models.ManyToManyField(UserProfile)
    updated = models.DateField()
    def __str__(self):
        return self.title

class Summary(models.Model):
    title = models.TextField(blank=True)
    text = models.TextField()
    url = models.URLField(blank=True)
    topics = models.ManyToManyField(Topic)
    def __str__(self):
        return self.text
