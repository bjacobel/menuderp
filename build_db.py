from datetime import datetime  # I fucking hate modules like this
import requests
import re

today = datetime.today()
locations = {
    "Moulton": 48,
    "Thorne": 49,
}

if today.weekday() is (5 or 6):
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

            # remove everything up to the first header
            html = re.split(r'<h3>', html)
            html.pop(0)

            # fuck express meal
            for meal in html:
                if re.search("Express Meal", meal):
                    html.remove(meal)

                # grab the food group (main course, soup, vegetable, etc)
                foodgroup = re.split('<span>', meal)[0]

                foods = re.split('<span>', meal)[1:]
                for food in foods:
                    
