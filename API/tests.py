from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model 
from rest_framework.test import APITestCase
from rest_framework import status 

# Create your tests here.
User = get_user_model()


class UserTest(APITestCase):
    
    def setUp(self):
        self.test_user = User.objects.create_user('usertest','test@gmail.com', 'testing123')
        self.create_url = reverse('api-register')

    def test_create_user(self):
        data={

            'username':'example',
            'email':'example@gmail.com',
            'password':'random123',
        }
        response = self.client.post(self.create_url, data, format=None)
        self.assertEqual(User.objecself.assertEqual(response.data['username'], data['username']))
        self.assertEqual(response.data['email'], data['email'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.assertFalse('password' in response.data )
    
    def test_create_user_with_no_email(self):
        data={
            'username':'example',
            'email':'',
            'password':'random123',
        }
        response = self.client.post(self.create_url, data, format=None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(),1)
        self.assertEqual(len(response.data['email']),1)

    def test_create_user_with_invalid_email(self):
        data={
            'username':'example',
            'email':'something',
            'password':'random123',
        }
        response = self.client.post(self.create_url, data, format=None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(),1)
        self.assertEqual(len(response.data['email']), 1)

    def test_create_user_with_existing_email(self):
        data={
            'username':'example',
            'email':'test@gmail.com',
            'password':'random123',
        }
        response = self.client.post(self.create_url, data, formay=None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(),1)
        self.assertEqual(len(response.data['email']), 1)

        def update_user(self):
            data={
            'username':'usertest',
            'email':'test@gmail.com',
            'password':'random123',
        }
        self.create_url = reverse('parentprofile-detail')
        response = self.client.put(self.create_url,data, format=None )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse('password' in response.data)
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])
        self.assertEqual(User.objects.count(), 1)