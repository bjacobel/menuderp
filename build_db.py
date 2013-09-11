from datetime import datetime  # I fucking hate modules like this
import requests
import re
from apps.menus import models as menu_models

today = datetime.today()
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

                        new_hash = hash(food + attrs)

                        if new_hash in menu_models.Food.objects.filter(_hash=new_hash):
                            #it's a food we've seen before
                            pass
                        else:
                            # it's a brand new food
                            new_food = menu_models.Food(name=food, attrs=attrs, last_date=today, next_date=today, location=value, meal=meal, foodgroup=foodgroup, _hash=hash(food+attrs))