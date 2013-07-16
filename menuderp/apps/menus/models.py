from django.contrib.auth.models import User
from django.db import models


class Food (models.Model):
    name = models.CharField(max_length=50)
    last_date = models.DateField()
    next_date = models.DateField()

    def __unicode__(self):
        return self.name


# Class to wrap django.contrib.auth's Users
class Profile (models.Model):
    user = models.ForeignKey(User)
    pro = models.BooleanField()
    used_watches = models.IntegerField(default=0)

    def username(self):
        return self.user.get_username()

    def firstname(self):
        return self.user.first_name

    def lastname(self):
        return self.user.last_name

    def fullname(self):
        return self.user.get_full_name()

    def email(self):
        return self.user.email

    def __unicode__(self):
        return self.username()

    def can_create_new_watches(self):
        if self.pro or self.used_watches < 5:
            return True
        return False


class Watch (models.Model):
    food = models.ForeignKey(Food)
    owner = models.ForeignKey(Profile)

    # days per week the alert should go out
    # 1 = sunday night
    # 3 = sunday night, wednesday night, friday night
    # 7 = every night
    # TODO: custom times (with Pro only)
    frequency = models.IntegerField()

    def frequency_name(self):
        if self.frequency is 1:
            return "weekly"
        elif self.frequency is 3:
            return "tri-weekly"
        elif self.frequency is 7:
            return "daily"
        else:
            return "custom"

    def __unicode__(self):
        return self.frequency_name() + " watch for " + self.food.__unicode__()

    class Meta:
        verbose_name_plural = "Watches"



