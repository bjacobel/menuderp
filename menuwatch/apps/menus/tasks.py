from celery import task
from datetime import datetime
import requests

@task()
def build_db():
    pass
    # Grab the next week's worth of food and add it to the database.
    # Test for success, then delete the last week's worth. 


