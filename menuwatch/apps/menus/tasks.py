from celery import task
from apps.menus import models as menus_models
from django.core.mail import EmailMultiAlternatives, send_mail
from django.shortcuts import render_to_response
from django.db import transaction
from urllib import urlencode
from datetime import date, timedelta
from hashlib import md5
from bs4 import BeautifulSoup
import requests
import re


# take food specialty attributes (V, GF, Display) 
# and return them separate from the food name
def parse_food_attrs(food):

    # first off, just remove "(Display) and - Display". Nobody cares if it's a display food!
    # Sorry. Pet peeve.
    food = re.sub(r'[\(\ -]*Display[\)\ -]*', '', food, flags=re.IGNORECASE)

    attrs = ""
    for attr in re.findall(r'\([A-Z]+\)', food):
        attrs += "{}, ".format(attr[1:-1])
    attrs = attrs[:-2]

    # remove them from the food, leaving just the title
    food = re.sub(r'\([A-Z]+\)', '', food)

    # also remove the weird spacing they sometimes give things
    food = re.sub(r'\ {2,}', ' ', food)

    return (food, attrs)


#@transaction.commit_manually
@task()
def build_db(lookahead=14):
    
    updated_foods = []
    
    today = date.today() + timedelta(days=lookahead)
    
    locations = {
        "Moulton": 48,
        "Thorne": 49,
    }

    if today.isoweekday() is (6 or 7):
        meals_available_today = ["Brunch", "Dinner"]
    else:
        meals_available_today = ["Breakfast", "Lunch", "Dinner"]
    
    for location, number in locations.iteritems(): 
        
        for meal in meals_available_today:

            payload = {
                "unit": number,  # number of hall
                "meal": meal,
                "mo": today.month-1,
                "dy": today.day,
                "yr": today.year,
            }

            r = requests.get('http://www.bowdoin.edu/atreus/views', params=payload)

            if r.status_code is 200:
                text = re.sub(r"<br>", "<br></br>", r.text)  # unclosed brs were throwing off BS4's sibling function
                soup = BeautifulSoup(text)

                foodgroups = soup.find_all("h3")
                foods = soup.find_all("span")

                menu = {}

                for foodgroup in foodgroups:
                    foodgroup_name = unicode(foodgroup.string)

                    if foodgroup_name != "Express Meal":
                        menu[foodgroup_name] = []
                        
                        for sibling in foodgroup.next_siblings:
                            
                            # foodgroups and food aren't properly nested, so this will kick over into
                            # a new course when it begins by breaking the loop
                            if sibling in foodgroups:
                                break
                            elif sibling in foods:
                                food_name = unicode(sibling.string)
                                menu[foodgroup_name].append(food_name)


                for (foodgroup, menu_foods) in menu.items():
                    
                    for menu_food in menu_foods:

                        (name, attrs) = parse_food_attrs(menu_food)

                        # generally good policy to do this any time I'm hitting the database in a loop, I think
                        sID = transaction.savepoint()
                        try:
                            (food, created) = menus_models.Food.objects.get_or_create(name__exact=name, attrs__exact=attrs)

                            food.name = name
                            food.attrs = attrs
                            food.location = location
                            food.meal = meal
                            food.foodgroup = foodgroup
                            food.push_next_date(today)

                            food.save()
                        except:
                            transaction.savepoint_rollback(sID)
                            raise
                        else:
                            transaction.commit()

                        updated_foods.append(food)
    return updated_foods



# update the dates once a day so that old "upcoming" foods aren't anymore
@transaction.commit_manually
@task()
def date_update(date_today=date.today()):
    for food in menus_models.Food.objects.exclude(next_dates=None):
        sID = transaction.savepoint()
        try:
            while food.peek_next_date() is not None and food.peek_next_date() < date_today:  # the food was offered yesterday or before
                popped_date = menus_models.FoodDate(date=food.pop_next_date())
                popped_date.save()
                food.last_date = popped_date  # pop from the front of the array
            food.save()
        except:
            transaction.savepoint_rollback(sID)
            raise
        else:
            transaction.commit()



@task()
def build_db_future(days):
    for i in xrange(days):
        build_db(i)


@task()
def mailer(dryrun=False):
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
    all_users = menus_models.Profile.objects.all()
    all_foods = menus_models.Food.objects.all()
    upcoming_soon = []
    upcoming_week = []
    upcoming_today = []

    for food in all_foods:
        if food.peek_next_date():
            if (sunday or wednesday or friday) and food.peek_next_date() <= today + timedelta(days=timedel):
                upcoming_soon.append(food)
            if sunday and food.peek_next_date() <= today + timedelta(days=7):
                upcoming_week.append(food)
            if food.peek_next_date() == today:
                upcoming_today.append(food)

    all_upcoming_foods = []

    for user in all_users:
        this_users_upcoming_foods = []
        pref_locs = ["Thorne", "Moulton", "Both"]
        if user.locations is 2:
            pref_locs = pref_locs.remove("Thorne")
        elif user.locations is 3:
            pref_locs = pref_locs.remove("Moulton")

        for watch in user.my_watches():
            if watch.food.location in pref_locs:
                if int(user.frequency) is 1 and sunday:
                    if watch.food in upcoming_week:
                        this_users_upcoming_foods.append(watch.food)
                elif int(user.frequency) is 3 and (sunday or wednesday or friday):
                    if watch.food in upcoming_soon:
                        this_users_upcoming_foods.append(watch.food)
                elif int(user.frequency) is 7:
                    if watch.food in upcoming_today:
                        this_users_upcoming_foods.append(watch.food)
                elif dryrun:  # fudge things a little if we're running tests: it doesn't matter if it's sunday or how frequent our fake users want to see alerts
                    if watch.food in upcoming_week:
                        this_users_upcoming_foods.append(watch.food)

                    
        if this_users_upcoming_foods and not dryrun:
            send_email(this_users_upcoming_foods, user)

        all_upcoming_foods += this_users_upcoming_foods

    if not dryrun:
        send_mail(
            "Menuwatch mailer successful",
            "Just mailed out {} alerts. Here they are:\n\n {}".format(len(all_upcoming_foods), all_upcoming_foods),
            "Menuwatch <mail@menuwat.ch>",
            ["Brian Jacobel <bjacobel@gmail.com>",],
        )

    return all_upcoming_foods


def send_email(alerted_foods, user):
    context = {
        'first_name': user.firstname(),
        'unsubscribe_link': urlencode({'u':user.email, 't':md5(user.user.date_joined.isoformat()).hexdigest()}),
        'email_type': 'alert',
        'item_list': sorted(alerted_foods, key=lambda x: x.peek_next_date(), reverse=True)
    }

    alerted_foods_as_string = ""
    for food in alerted_foods:
        alerted_foods_as_string += "{} on {} for {} at {}\n".format(food.name, food.next_date_readable(), food.meal, food.location)

    msg = EmailMultiAlternatives(
        "Coming soon: {} and more".format(alerted_foods[0].name),
        "Hi, {}! Here's a taste of what's coming up in the next few days: \n{}".format(context['first_name'], alerted_foods_as_string),
        "Menuwatch <mail@menuwat.ch>",
        ["{} <{}>".format(user.fullname(), user.email()),],
    )
    msg.attach_alternative(render_to_response('menus/email.html', context).content, "text/html")
    msg.send()


@task
def test_task():
    send_mail(
        "Test",
        "If you got this, it means that Celery is working.",
        "Menuwatch <mail@menuwat.ch>",
        ["Brian Jacobel <bjacobel@gmail.com>",],
    )



