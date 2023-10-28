# Required libraries/modules for testing
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
import json

# Create a test case class for the User Registration View
class RegisterUserViewTest(APITestCase):

    # Set up the initial data and configurations needed for the tests
    def setUp(self):
        # URL for the register endpoint, 'register' is the name of the URL pattern
        self.register_url = reverse('register')

        # Sample user data for testing
        self.user_data = {
            "username": "testuser",
            "password": "testpass",
            "email": "testuser@test.com"
        }

        # Getting the user model
        self.User = get_user_model()

    # Test case to ensure user registration is successful with valid data
    def test_register_user_success(self):
        """
        Ensure we can register a new user with valid data.
        """
        # Send a POST request to the register endpoint with the sample user data
        response = self.client.post(self.register_url, self.user_data, format='json')

        # Check if the user has been created in the database using the provided email
        user = self.User.objects.filter(email=self.user_data["email"]).first()

        # Ensure the response returns a 201 status code indicating successful creation
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if the registered user's username matches the provided username
        self.assertEqual(user.username, self.user_data["username"])

        # Ensure the password for the user matches the one provided. The check_password method is used as passwords are stored in a hashed format
        self.assertTrue(user.check_password(self.user_data["password"]))

        # Future implementation: check if response contains authentication tokens and validate them

    # Test case to check that registration fails if the username already exists
    def test_register_user_existing_username(self):
        """
        Ensure we cannot register a user with an existing username.
        """
        # Create a user with the sample data to simulate a pre-existing user scenario
        self.User.objects.create_user(**self.user_data)

        # Try to register a user again with the same data
        response = self.client.post(self.register_url, self.user_data, format='json')

        # The response should be a 400 status code indicating a bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Ensure the error message matches the expected error structure.
        self.assertEqual(json.loads(response.content), {'detail': ['Choose another email.']})

    # More test cases can be added here to check for other edge cases 
    # e.g., registration with invalid email, short password, missing fields etc.
