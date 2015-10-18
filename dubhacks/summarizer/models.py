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
    updated = models.DateField(blank=True, null=True)
    def __str__(self):
        return self.title
    def was_updated_today(self):
        return self.updated >= timezone.now() - datetime.timedelta(days=1)

class Summary(models.Model):
    title = models.TextField(blank=True)
    text = models.TextField()
    url = models.URLField(blank=True)
    topics = models.ManyToManyField(Topic)
    def __str__(self):
        return self.text
