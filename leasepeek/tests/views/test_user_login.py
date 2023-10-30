# Required libraries/modules for user login testing
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
import json
import jwt
from rest_framework_simplejwt.tokens import AccessToken

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
        self.User = get_user_model()

    def create_test_user(self):
        """
        Helper method to create a new user.
        """
        # Send a POST request to the register endpoint with the sample user data
        response = self.client.post(self.register_url, self.user_data, format='json')

        # Check if the user has been created in the database using the provided email.
        user = self.User.objects.filter(email=self.user_data["email"]).first()

        # Ensure the response returns a 201 status code indicating successful creation
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check if the registered user's username matches the provided username
        self.assertEqual(user.username, self.user_data["username"])
        print("USER LOGIN TEST")