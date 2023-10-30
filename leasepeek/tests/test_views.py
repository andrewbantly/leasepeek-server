# Required libraries/modules for testing
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
import json
import jwt
from rest_framework_simplejwt.tokens import AccessToken
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

        # Check if the user has been created in the database using the provided email. Because `filter()` returns a QuerySet, which can contain any number of results, even if one item to match the query is expected, `filter()` won't return a single object. The `first()` method returns the first object matched by the queryset, or `None`.
        user = self.User.objects.filter(email=self.user_data["email"]).first()

        # Ensure the response returns a 201 status code indicating successful creation
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if the registered user's username matches the provided username
        self.assertEqual(user.username, self.user_data["username"])

        # Ensure the password for the user matches the one provided. The check_password method is used as passwords are stored in a hashed format
        self.assertTrue(user.check_password(self.user_data["password"]))

        # Check if the access and refesh tokens are in the response
        self.assertIn('refresh', response.data, "Refresh token not found in the response data")
        self.assertIn('access', response.data, "Access token not found in the response data")

       # Get the access token from the response data
        access_token = response.data['access']

        # Validate the access token. The verification and decoding is handled by the AccessToken class from django-rest-framework-simplejwt
        try:
            # Decode the access token
            access_token_obj = AccessToken(access_token)

            # Username claim check
            self.assertEqual(access_token_obj['username'], user.username, "Token's username does not match the created user's username") 

            logger.info(f"User {user.username} verified through JWT Access Token.")

        except jwt.ExpiredSignatureError:
            self.fail("Access token is expired")
        except jwt.InvalidTokenError:
            self.fail("Invalid access token")


    # Test case to check that registration fails if the username already exists
    def test_register_user_existing_username(self):
        """
        Ensure we cannot register a user with an existing username.
        """
        # Create a user with the sample data to simulate a pre-existing user scenario
        self.User.objects.create_user(**self.user_data)

         # Modify the user_data to change the email while keeping the username the same
        new_user_data = self.user_data.copy()
        new_user_data['email'] = 'new_user_email@example.com'

        # Try to register a user again with the same username, different email
        response = self.client.post(self.register_url, new_user_data, format='json')

        # The response should be a 400 status code indicating a bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Ensure the error message matches the expected error structure.
        self.assertEqual(json.loads(response.content), {'detail': ['Choose another username.']})

    def test_register_user_no_username(self):
        """
        Ensure we cannot register a user without a username
        """
         # Create unique user data without a username
        user_register_data = {
            "username": "",
            "password": "testfail",
            "email": "testnouser@test.com"
        }

        # Try to register a user without a username
        response = self.client.post(self.register_url, user_register_data, format='json')

        # The response should be a 400 status code indicating a bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Ensure the error message matches the expected error structure
        self.assertEqual(json.loads(response.content), {'detail': ['Choose another username.']})

    def test_register_user_existing_email(self):
        """
        Ensure we cannot register a user with an existing email.
        """
        # Create a user with the sample data to simulate a pre-existing user scenario
        self.User.objects.create_user(**self.user_data)

        # Send a POST request to the register endpoint with the sample user data
        response = self.client.post(self.register_url, self.user_data, format='json')

        # The response should be a 400 status code indicating a bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Ensure the error message matches the expected error structure
        self.assertEqual(json.loads(response.content), {'detail': ['Choose another email.']})

    def test_register_user_no_email(self):
        """
        Ensure we cannot register a user without an email address
        """
         # Create unique user data without a username
        user_register_data = {
            "username": "testnoemail",
            "password": "testfail",
            "email": ""
        }

        # Try to register a user without a username
        response = self.client.post(self.register_url, user_register_data, format='json')

        # The response should be a 400 status code indicating a bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Ensure the error message matches the expected error structure
        self.assertEqual(json.loads(response.content), {'detail': ['Choose another email.']})

    def test_register_user_no_password(self):
        """
        Ensure we cannot register a user without a valid password. The applications require a password to be eight characters or longer.
        """
        #  Create unique user data without a password
        user_register_data = {
            "username": "testnopassword",
            "password": "",
            "email": "testnopassword@test.com"
        }

        # Try to register a user without a password
        response = self.client.post(self.register_url, user_register_data, format='json')

        # The response should be a 400 status code indicating a bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Ensure the error message matches the expected error structure
        self.assertEqual(json.loads(response.content), {'detail': ['Choose another password, min 8 characters.']})

    def test_register_user_invalid_password(self):
        """
        Ensure we cannot register a user without a valid password. The applications require a password to be eight characters or longer.
        """
        #  Create unique user data without a password
        user_register_data = {
            "username": "testnopassword",
            "password": "sm_pass",
            "email": "testnopassword@test.com"
        }

        # Try to register a user without a password
        response = self.client.post(self.register_url, user_register_data, format='json')

        # The response should be a 400 status code indicating a bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Ensure the error message matches the expected error structure
        self.assertEqual(json.loads(response.content), {'detail': ['Choose another password, min 8 characters.']})


    # More test cases can be added here to check for other edge cases 
    # e.g., registration with invalid email, short password, missing fields etc.
