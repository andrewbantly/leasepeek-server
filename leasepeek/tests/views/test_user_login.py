# Required libraries/modules for user login testing
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
import json
import jwt
from rest_framework_simplejwt.tokens import AccessToken
import logging

logger = logging.getLogger(__name__)

# Create a test case class for the User Login View
class LoginUserViewTest(APITestCase):

    # Set up the initial data and configurations needed for the tests
    def setUp(self):
        # URL for the register and login endpoint
        self.register_url = reverse('register')
        self.login_url = reverse('login')

        self.user_data = {
            'username': 'testloginuser',
            'email': 'testlogin@test.com',
            'password': 'testpassword123'
        }
        # Getting the user model
        self.User = get_user_model()

        self.client.post(self.register_url, self.user_data, format='json')

    def test_login_with_valid_credentials(self):
        response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)