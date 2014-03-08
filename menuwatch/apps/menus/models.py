from django.contrib.auth.models import User
from django.db import models
from datetime import date, timedelta
import re

class FoodDate (models.Model):
    date = models.DateField(null=True, blank=True)

    # return a short, human-readable description of the date
    def readable(self):
        if self.date is None:  # don't know why it would ever be, but w/e
            return "Unknown"
        elif self.date == date.today():
            return "Today"
        elif self.date > date.today():
            if self.date == date.today()+timedelta(days=1):
                return "Tomorrow"
            elif self.date > date.today()+timedelta(days=1) and self.date < date.today()+timedelta(days=6):
                return self.date.strftime("%A")
            else:
                return self.date.strftime("%b %d")
        elif self.date < date.today():
            if self.date == date.today()-timedelta(days=1):
                return "Yesterday"
            elif self.date == date.today()-timedelta(days=2):
                return "Two days ago"
            elif self.date < date.today()+timedelta(days=2) and self.date > date.today()-timedelta(days=6):
                return "Last " + self.date.strftime("%A")
            else:
                return self.date.strftime("%b %d")

    # return the date as YYYY-MM-DD
    def __unicode__(self):
        return self.date.isoformat()


class Food (models.Model):
    # fixed
    name = models.CharField(max_length=100)
    attrs = models.CharField(max_length=25, blank=True)  # my logic here being that the vegan and non-vegan versions of a food are not really the same thing at all

    # variable
    last_date = models.ForeignKey(FoodDate, null=True, related_name='last_date_food_was_offered')
    next_dates = models.ManyToManyField(FoodDate, null=True, related_name='upcoming_dates_for_food')
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
        return self.watch_set.count()

    def watchers(self):
        watchers = []
        for watch in self.watch_set.all():
            watchers.append(watch.owner.user)
        return watchers

    # push/pop/peek is an anachronism that explains what I'm achieving, not what I'm doing

    def push_next_date(self, date):  # add a future date, return the queryset of all
        (found_date, created) = FoodDate.objects.get_or_create(date=date)
        found_date.save()
        self.next_dates.add(found_date)
        return self.next_dates.all()

    def pop_next_date(self):  # pop and return the true next date
        try:
            next = self.next_dates.all().order_by('date')[:1].get()
            next.delete()
            return next.date
        except:
            return None

    def peek_next_date(self):  # peek at the true next date
        try:
            return self.next_dates.all().order_by('date')[:1].get().date
        except:
            return None

    def next_date_readable(self):
        try:
            return self.next_dates.all().order_by('date')[:1].get().readable()
        except:
            return "Unknown"

    def last_date_readable(self):
        try:
            return self.last_date.readable()
        except:
            return "Ages ago"

    def __unicode__(self):
        return self.name

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
    onboarded = models.BooleanField(default=False)

    def used_watches(self):
        return self.my_watches().count()

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
