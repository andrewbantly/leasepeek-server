# Required libraries/modules for testing custom token authentication endpoints

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
import json
import jwt
from rest_framework_simplejwt.tokens import AccessToken

class CustomTokenObtainPairViewTest(APITestCase):
    
    def setUp(self):
       # URL for the register endpoint
        self.token_url = reverse('token_obtain_pair')

        # Getting the user model
        self.User = get_user_model()

        # Create a test user
        self.user = self.User.objects.create_user(username="testusertoken", email="testusertoken@test.com", password="testpass")



    def test_custom_token_obtain_pair(self):
        """
        Ensure we can obtain a token pair with valid credentials using the custom token view.
        """
        # Define the payload with correct credentials
        payload = {
            "email": "testusertoken@test.com",
            "password": "testpass"
        }

        # Make a POST request to the token obtain pair endpoint
        response = self.client.post(self.token_url, payload, format='json')

        # Assert that the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that an access and refresh tokens were included in the response
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)