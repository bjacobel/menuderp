# Menuwatch


### The menu tracker for Bowdoin students.

Do you love Hungarian Mushroom Soup, but always forget and go to Thorne when it's at Moulton? 

Does finding out that there's Taco Bar on Thursday totally make your week?

**Menuwatch is for you.**

***

* Track your favorite menu items at Moulton and Thorne and recieve email alerts when they're coming up
* Customize your alerts: see the next day, three days, or week at a glance. Don't ever go to Moulton? Enable alerts for Thorne only.
* See what foods are recent or popular, and add them to your alerts instantly

***
Menuwatch is a Django 1.5 app. To get started, ensure that you have Python 2.7.x, clone this repo, then `pip install -r reqs/dev.txt`. Install Postgres (the reccommended way is with [Postgres.app](http://postgresapp.com/)) and create a database named `menuwatch`. After you `manage.py syncdb` and `manage.py migrate`, you'll be able to `manage.py runserver` to get up and running. 
