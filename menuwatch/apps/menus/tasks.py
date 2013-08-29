from celery import task
from datetime import date, timedelta
from apps.menus import models as menu_models
from hashlib import md5
import requests
import re
import sys

@task()
def build_db(lookahead=0):
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
                                
                                old_food.push_next_date(today)  # stick on the end of the array

                                old_food.save()
                            else:
                                # it's a brand new food
                                new_food = menu_models.Food(name=food, attrs=attrs, location=key, meal=meal, foodgroup=foodgroup)
                                new_food.push_next_date(today)
                                new_food.save()


@task()
def build_db_future(days):
    for i in xrange(0, days):
        build_db(i)
    
@task()
def sync_food_dates():
    for food in menu_models.Food.objects.filter(peek_next_date__exact=date.today()):
        food.last_date = old_food.pop_next_date()  # pop from the front of the array

