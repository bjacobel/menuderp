from celery import task
from datetime import date, timedelta
from apps.menus import models as menu_models
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render_to_response
from django.db import transaction
from hashlib import md5
from urllib import urlencode
import requests
import re

@transaction.commit_manually
@task()
def build_db(lookahead=28):
    today = date.today() + timedelta(days=lookahead)
    locations = {
        "Moulton": 48,
        "Thorne": 49,
    }

    if today.isoweekday() is (6 or 7):
        meals_available_today = ["Brunch", "Dinner"]
    else:
        meals_available_today = ["Breakfast", "Lunch", "Dinner"]

    for key, value in locations.iteritems():
        for meal in meals_available_today:

            payload = {
                "unit": value,  # number of hall
                "meal": meal,
                "mo": today.month-1,
                "dy": today.day,
                "yr": today.year,
            }

            r = requests.get('http://www.bowdoin.edu/atreus/views', params=payload)

            if r.status_code is 200:
                html = r.text

                # remove <br>, \n, </h3>, </span>, </html>, </body>s
                html = re.sub(r'\n|<br>|</h3>|</span>|</html>|</body>', "", html)

                # their utf-8 is broken, probably in more ways than just this
                html = re.sub(r'&amp;', '&', html)

                # remove everything up to the first header
                html = re.split(r'<h3>', html)
                html.pop(0)

                # fuck express meal
                for meal_chunk in html:
                    if not re.search("Express Meal", meal):

                        # grab the food group (main course, soup, vegetable, etc)
                        foodgroup = re.split('<span>', meal_chunk)[0]

                        foods = re.split('<span>', meal_chunk)[1:]
                        for food in foods:

                            # grab the food specialty attributes (ve, gf)
                            attrs = ""
                            match = re.search(r'\(.+\)', food)
                            if match:
                                attrs = match.group()
                                attrs = re.sub(r'\(', '', attrs)
                                attrs = re.sub(r'\)', ', ', attrs)[:-2]

                            # then remove them
                            food = re.sub(r'\(.+\)', '', food)

                            new_hash = md5(food + attrs).hexdigest()

                            try:
                                old_food = menu_models.Food.objects.get(myhash__exact=new_hash)
                            except: 
                                old_food = None

                            if old_food is not None:
                                #it's a food we've seen before
                                old_food.location = key
                                old_food.meal = meal
                                old_food.foodgroup = foodgroup

                                try:
                                    most_recent_date_found = old_food.next_date_array[-1]
                                    if most_recent_date_found != today:
                                        old_food.push_next_date(today)  # stick on the end of the array
                                except:
                                    pass

                                old_food.save()
                            else:
                                # it's a brand new food
                                sID = transaction.savepoint()
                                try:
                                    new_food = menu_models.Food(name=food, attrs=attrs, location=key, meal=meal, foodgroup=foodgroup)
                                    new_food.push_next_date(today)
                                    new_food.save()
                                except:  # they goofed something in the menu formatting. IDGAF. Drop it.
                                    transaction.savepoint_rollback(sID)

    # sync the dates
    for food in menu_models.Food.objects.exclude(next_date_array=[]):
        if food.peek_next_date() < date.today():  # the food was offered yesterday or before
            food.last_date = food.pop_next_date()  # pop from the front of the array
            food.save()

    transaction.commit()


@task()
def build_db_future(days):
    for i in xrange(0, days):
        build_db(i)


@task()
def mailer():
    today = date.today()
    weekday = today.isoweekday()

    # a little fudging so I can write semantic if statements later
    sunday = False
    wednesday = False
    friday = False
    if weekday is 7:
        sunday = True
        timedel=3
    elif weekday is 3:
        wednesday = True
        timedel=2
    elif weekday is 5:
        friday = True
        timedel=2

    # get some querysets
    all_users = menu_models.Profile.objects.all()
    if sunday or wednesday or friday:
        upcoming = menu_models.Food.objects.filter(peek_next_date__lte=today+timedelta(days=timedel))
    elif sunday:
        upcoming = menu_models.Food.objects.filter(peek_next_date__lte=today+timedelta(days=7))
    else:
        upcoming = menu_models.Food.objects.filter(peek_next_date__exact=today)

    raised_alerts = []

    for user in all_users:
        pref_locs = ["Thorne", "Moulton"]
        if user.locations is 2:
            pref_locs = pref_locs.remove("Thorne")
        elif user.locations is 3:
            pref_locs = pref_locs.remove("Moulton")
        if (user.frequency is 1 and sunday) or (user.frequency is 3 and (sunday or wednesday or friday)) or (user.frequency is 7):
            for watch in user.my_watches:
                if watch.food in upcoming and watch.food.location in pref_locs:
                    raised_alerts.append(watch.food)
            send_email(raised_alerts, user)

def send_email(raised_alerts, user):
    context = {
        'first_name': user.first_name,
        'unsubscribe_link': urlencode({'u':user.email, 't':md5(user.date_joined.isoformat()).hexdigest()}),
        'email_type': 'alert',
        'item_list': sorted(raised_alerts, key=lambda x: x.peek_next_date(), reverse=True)
    }
    msg = EmailMultiAlternatives(
        "Menuwatch Signup Confirmation",
        "Hi, {}! Menuwatch doesn't really support non-HTML email clients, but here's a taste of what's coming up in the next few days: {}".format(context['first_name'], context['raised_alerts']),
        "Menuwatch <mail@menuwat.ch>",
        ["{} {} <{}>".format(user.first_name, user.last_name, user.email),],
    )
    msg.attach_alternative(render_to_response('menus/email.html', context), "text/html")
    msg.content_subtype = "html"
    msg.send()




