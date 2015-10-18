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
	def __str__(self):
		return self.title

class Summary(models.Model):
	text = models.TextField()
	date = models.DateTimeField('date updated')
	topics = models.ManyToManyField(Topic)
	def __str__(self):
		return self.text
