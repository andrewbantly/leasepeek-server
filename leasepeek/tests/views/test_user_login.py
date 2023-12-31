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

        # Getting the user model
        self.User = get_user_model()

        # Create test login user
        self.user = self.User.objects.create_user(username='testloginuser', email='testlogin@test.com', password='testpassword123')        

    # Test case to ensure user login is successful with valid data
    def test_login_with_valid_credentials(self):

        # Send a POST request to the login endpoint with the sample user data
        response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        # Ensure the response returns a 200 status code indicating login successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the user has been created in the database using the provided email.      
        user = self.User.objects.filter(email=self.user_data["email"]).first()

        # Ensure the login response includes username & email data
        self.assertIn('username', response.data, "Username not found in the response data")
        self.assertIn('email', response.data, "Email not found in the response data")

        # Check if the registered user's username & email matches the provided username & email
        self.assertEqual(user.username, self.user_data["username"])
        self.assertEqual(user.email, self.user_data["email"])

        # Check if the registered user's username & email matches the response username & email
        self.assertEqual(self.user.username, response.data["username"])
        self.assertEqual(self.user.email, response.data["email"])

        # Ensure the response does not include a user's password
        self.assertNotIn('password', response.data, "Password is found in the response data")

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

        except jwt.ExpiredSignatureError:
            self.fail("Access token is expired")
        except jwt.InvalidTokenError:
            self.fail("Invalid access token")

    def test_login_with_invalid_email(self):
        # Modify the user data to include an invalid email
        invalid_user = self.user_data.copy()
        invalid_user['email'] = 'invalid_email@test.com'

        # Try and login a user with an invalid email
        response = self.client.post(self.login_url, invalid_user, format='json')

        # The response should be a 400 status code indicating a bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Ensure the error message matches the expected error structure
        self.assertEqual(json.loads(response.content), {'detail': 'user not found'})

    def test_login_with_invalid_password(self):
        # Modify the user data to include an invalid password
        invalid_user = self.user_data.copy()
        invalid_user['password'] = 'badpassword'

        # Try and login a user with an invalid password
        response = self.client.post(self.login_url, invalid_user, format='json')
        
        # The response should be a 400 status code indicating a bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Ensure the error message matches the expectted error structure
        self.assertEqual(json.loads(response.content), {'detail': 'user not found'})
