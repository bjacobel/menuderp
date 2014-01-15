from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from apps.menus import models as menus_models
from apps.menus import tasks as menus_tasks
from datetime import date, timedelta
 
class APITest(TestCase):
    def test_add_endpoint(self):
        c = Client()

        self.assertEqual(c.get('/api/add').status_code, 418) # i'm a teapot
        
        self.assertEqual(c.post('/api/add').status_code, 403) # no authenticated user present
        
        u = User.objects.create_user('test@case.com', 'test@case.com', 'testcasepassword')
        c.login(username='test@case.com', password='testcasepassword')

        self.assertEqual(c.post('/api/add').status_code, 400)  # no food_pk specified

        p = menus_models.Profile(user=u)
        p.save()

        self.assertEqual(c.post('/api/add', {'food_pk': 1}).status_code, 404)  # specified food does not exist

        f1 = menus_models.Food(name="f1"); f1.save()
        f2 = menus_models.Food(name="f2"); f2.save()
        f3 = menus_models.Food(name="f3"); f3.save()
        f4 = menus_models.Food(name="f4"); f4.save()
        f5 = menus_models.Food(name="f5"); f5.save()
        f6 = menus_models.Food(name="f6"); f6.save()

        self.assertEqual(c.post('/api/add', {'food_pk': f1.pk}).status_code, 201)
        self.assertEqual(c.post('/api/add', {'food_pk': f2.pk}).status_code, 201)
        self.assertEqual(c.post('/api/add', {'food_pk': f3.pk}).status_code, 201)
        self.assertEqual(c.post('/api/add', {'food_pk': f4.pk}).status_code, 201)
        self.assertEqual(c.post('/api/add', {'food_pk': f5.pk}).status_code, 201)
        # normal user runs out of watches at 5
        self.assertEqual(c.post('/api/add', {'food_pk': f6.pk}).status_code, 431)


    def test_delete_endpoint(self):
        c = Client()

        self.assertEqual(c.get('/api/delete').status_code, 418) # i'm a teapot
        
        self.assertEqual(c.post('/api/delete').status_code, 403) # no authenticated user present

        u = User.objects.create_user('test@case.com', 'test@case.com', 'testcasepassword')
        c.login(username='test@case.com', password='testcasepassword')
        self.assertEqual(c.post('/api/delete').status_code, 400) # no food_pk specified

        self.assertEqual(c.post('/api/delete', {"food_pk": 1}).status_code, 404) # no watch matching those specs found

        p = menus_models.Profile(user=u)
        p.save()

        f1 = menus_models.Food(name="f1"); f1.save()
        self.assertEqual(c.post('/api/add', {'food_pk': f1.pk}).status_code, 201)

        self.assertEqual(c.post('/api/delete', {"food_pk": f1.pk}).status_code, 200)


    def test_settings_endpoint(self):
        c = Client()

        self.assertEqual(c.get('/api/settings').status_code, 418) # i'm a teapot
        
        self.assertEqual(c.post('/api/settings').status_code, 403) # no authenticated user present

        u = User.objects.create_user('test@case.com', 'test@case.com', 'testcasepassword')
        c.login(username='test@case.com', password='testcasepassword')
        self.assertEqual(c.post('/api/settings').status_code, 400) # no setting/value specified

        self.assertEqual(c.post('/api/settings', {'setting_name': 'pro', "setting_value": "true"}).status_code, 200)
        self.assertEqual(c.post('/api/settings', {'setting_name': 'location', "setting_value": 2}).status_code, 200)
        self.assertEqual(c.post('/api/settings', {'setting_name': 'frequency', "setting_value": 7}).status_code, 200)


class TasksTest(TestCase):
    # aquire foods ten days out for twenty days. Check foods left at the end. 
    def test_food_popping(self):

        # build database for the next month
        for i in xrange(30):
            menus_tasks.build_db(i)

        # now pretend it's 31 days from now; delete every food that's 'past'
        # should end up with every food being deleted (but doesn't!)
        menus_tasks.date_update(date.today() + timedelta(days=31))

        broken = []
        for food in menus_models.Food.objects.all():
            if food.peek_next_date() is not None and food.peek_next_date() < date.today() + timedelta(days=31):
                broken.append(food)

        self.assertEqual(len(broken), 0)
