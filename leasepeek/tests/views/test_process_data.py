# Required libraries/modules for testing data process endpoint
import os
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
import jwt
from rest_framework_simplejwt.tokens import AccessToken
from django.core.files.uploadedfile import SimpleUploadedFile

class ProcessDataViewTest(APITestCase):

    def setUp(self):
        # establish the end point
        self.process_data_url = reverse('process_data')
        self.login_url = reverse('login')

        # Get the User model
        self.User = get_user_model()
  
        # create a user
        self.user = self.User.objects.create_user(username='testuserdataprocess', email='testuserdataprocess@test.com', password='testpass')

    # Test good data with valid credentials
    def test_process_valid_data(self):
        user_data_payload = {
            'email': 'testuserdataprocess@test.com',
            'password': 'testpass'
        }

        # User needs to be logged in
        login_response = self.client.post(self.login_url, user_data_payload, format='json')

        # Ensure the login response returns a 200 status code indicating login successful
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Ensure the login response includes username & email data
        self.assertIn('username', login_response.data, "Username not found in the response data")
        self.assertIn('email', login_response.data, "Email not found in the response data")

        # Check if the registered user's username & email matches the response username & email
        self.assertEqual(self.user.username, login_response.data["username"])
        self.assertEqual(self.user.email, login_response.data["email"])

        # Ensure the response does not include a user's password
        self.assertNotIn('password', login_response.data, "Password is found in the response data")

        # Ensure the login response includes an access token
        self.assertIn('access', login_response.data, "Access token not found in the response data")
        self.assertIn('refresh', login_response.data, "Refresh token not found in the response data")

        # Get the Access token from the response data
        access_token = login_response.data['access']

        try:
            # Decode the access token
            access_token_obj = AccessToken(access_token)

            # Username claim check
            self.assertEqual(access_token_obj['username'], self.user.username, "Token's username does not match the created user's username")
            
        except jwt.ExpiredSignatureError:
            self.fail("Access token is expired")
        except jwt.InvalidTokenError:
            self.fail("Invalid access token")

        # Define the base directory for test data relative to this file's location
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Construct the path to the test file
        test_file_path = os.path.join(BASE_DIR, 'test_data', 'test.xlsx')

        # Open the file and read its content in binary mode
        with open(test_file_path, 'rb') as real_file:
            file_content = real_file.read()

        # Create a SimpleUploadedFile with content read from the real file
        file = SimpleUploadedFile(
                name="test.xlsx",
                content=file_content,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        response = self.client.post(self.process_data_url, {'file': file}, format='multipart', HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Check that the upload was successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        


    # test good data with invalid credentials
    # test bad data with valid credentials 
