from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import User

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('token_obtain_pair')
        
        # Test user data
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'user_type': 'CUSTOMER'
        }
        
        self.owner_data = {
            'username': 'testowner',
            'email': 'owner@example.com',
            'password': 'testpass123',
            'user_type': 'OWNER'
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_user_login(self):
        # Create user first
        self.client.post(self.register_url, self.user_data)
        
        # Attempt login
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
