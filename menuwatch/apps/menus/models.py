from django.contrib.auth.models import User
from django.db import models
from hashlib import md5
from datetime import date, timedelta
from picklefield.fields import PickledObjectField
import re


class Food (models.Model):
    # fixed
    name = models.CharField(max_length=100)
    attrs = models.CharField(max_length=25, blank=True)  # my logic here being that the vegan and non-vegan versions of a food are not really the same thing at all
    myhash = models.CharField(max_length=32,editable=False)

    # variable
    last_date = models.DateField(blank=True, null=True)
    next_date_array = PickledObjectField(default=[])
    location = models.CharField(max_length=7)
    meal = models.CharField(max_length=9)
    foodgroup = models.CharField(max_length=25)  # a food could get offered as a different group but we wouldn't want it to show up separately
   

    def is_vegan(self):
        return re.search('\s?V(,|$)', self.attrs)

    def is_vegetarian(self):
        return re.search('\s?VE(,|$)', self.attrs)

    def is_gluten_free(self):
        return re.search('\s?GF(,|$)', self.attrs)

    # I don't actually know what these last two mean
    def is_L(self):
        return re.search('\s?L(,|$)', self.attrs)

    def is_D(self):
        return re.search('\s?D(,|$)', self.attrs)

    def num_watches(self):
        return len(self.watch_set.all())

    def watchers(self):
        watchers = []
        for watch in self.watch_set.all():
            watchers.append(watch.owner.user)
        return watchers

    def push_next_date(self, date):  # add a future date to the end of the date array
        self.next_date_array = list(self.next_date_array) + [date,]
        return self.next_date_array

    def pop_next_date(self):  # pop and return the true next date
        try:
            return self.next_date_array.pop(0)
        except:
            return None

    def peek_next_date(self):  # peek at the true next date
        try:
            return self.next_date_array[0]
        except:
            return None

    def next_date_readable(self):
        if self.peek_next_date() is None:
            return "Unknown"
        elif self.peek_next_date() == date.today():
            return "Today"
        elif self.peek_next_date() == date.today()+timedelta(days=1):
            return "Tomorrow"
        elif self.peek_next_date() > date.today()+timedelta(days=1) and self.peek_next_date() < date.today()+timedelta(days=6):
            return self.peek_next_date().strftime("%A")
        else:
            return self.peek_next_date().strftime("%b %d")

    def last_date_readable(self):
        if self.last_date is None:
            return "Ages ago"
        elif self.last_date == date.today()-timedelta(days=1):
            return "Yesterday"
        elif self.last_date == date.today()-timedelta(days=2):
            return "Two days ago"
        elif self.last_date < date.today()+timedelta(days=2) and self.last_date > date.today()+timedelta(days=6):
            return "Last " + self.last_date.strftime("%A")
        else:
            return self.last_date.strftime("%b %d")

    def __unicode__(self):
        return self.name

    def save(self):
        self.myhash = md5(self.name + self.attrs).hexdigest()
        super(Food, self).save()

    num_watches.short_description = "Watched by"


class Watch (models.Model):
    food = models.ForeignKey('Food')
    owner = models.ForeignKey('Profile')

    def foodname(self):
        return self.food

    def frequency(self):
        return self.owner.frequency

    def __unicode__(self):
        return self.owner.__unicode__() + "'s watch for " + self.food.__unicode__()

    class Meta:
        verbose_name_plural = "Watches"


# Class to wrap django.contrib.auth's Users
class Profile (models.Model):
    user = models.ForeignKey(User)
    pro = models.BooleanField(default=False)
    frequency = models.IntegerField(default=1)
    locations = models.IntegerField(default=1)

    def used_watches(self):
        return len(self.my_watches())

    def my_watches(self):
        return self.watch_set.all()

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
        if self.pro or self.used_watches() < 10:
            return True
        return False

    def frequency_name(self):
        if self.frequency == 1:
            return "Weekly"
        elif self.frequency == 3:
            return "Tri-weekly"
        elif self.frequency == 7:
            return "Daily"

    def location_name(self):
        if self.locations == 1:
            return "Both"
        elif self.frequency == 2:
            return "Moulton Only"
        elif self.frequency == 3:
            return "Thorne Only"

    frequency_name.short_description = "Frequency"

    can_create_new_watches.boolean = True
    can_create_new_watches.short_description = "Has watches left?"
    used_watches.short_description = "Active Watches"
