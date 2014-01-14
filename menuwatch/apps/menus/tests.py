from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from apps.menus import models as menus_models
 
class APITest(TestCase):
    def test_add_endpoint(self):
        c = Client()
        response = c.get('/api/add')
        self.assertEqual(response.status_code, 418) # i'm a teapot
        
        response = c.post('/api/add')
        self.assertEqual(response.status_code, 403) # no authenticated user present
        
        u = User.objects.create_user('test@case.com', 'test@case.com', 'testcasepassword')
        c.login(username='test@case.com', password='testcasepassword')
        response = c.post('/api/add')
        self.assertEqual(response.status_code, 400)  # no food_pk specified

        p = menus_models.Profile(user=u)
        p.save()

        response = c.post('/api/add', {'food_pk': 1})
        self.assertEqual(response.status_code, 404)  # specified food does not exist

        f1 = menus_models.Food(name="f1"); f1.save()
        f2 = menus_models.Food(name="f2"); f2.save()
        f3 = menus_models.Food(name="f3"); f3.save()
        f4 = menus_models.Food(name="f4"); f4.save()
        f5 = menus_models.Food(name="f5"); f5.save()
        f6 = menus_models.Food(name="f6"); f6.save()

        self.assertEqual(c.post('/api/add', {'food_pk': 1}).status_code, 201)
        self.assertEqual(c.post('/api/add', {'food_pk': 2}).status_code, 201)
        self.assertEqual(c.post('/api/add', {'food_pk': 3}).status_code, 201)
        self.assertEqual(c.post('/api/add', {'food_pk': 4}).status_code, 201)
        self.assertEqual(c.post('/api/add', {'food_pk': 5}).status_code, 201)
        # normal user runs out of watches at 5
        self.assertEqual(c.post('/api/add', {'food_pk': 1}).status_code, 431)


class TasksTest(TestCase):
    # aquire foods ten days out for twenty days. Check foods left at the end. 
    def test_food_popping(self):
        self.assertEqual(0, 0)