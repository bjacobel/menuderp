from django.contrib.auth.models import User
from django.db import models


class Food (models.Model):
    name = models.CharField(max_length=50)
    last_date = models.DateField()
    next_date = models.DateField()


class Alert (models.Model):
    food = models.ForeignKey(Food)
    frequency = models.CharField(max_length=10)


class Profile (models.Model):
    user = models.ForeignKey(User)
