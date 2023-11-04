# Required imports for testing Read User Data endpoint
import os
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

class ReadUserDataViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # This method is called once before any test is run to set up data that's shared among all tests
        
        # Reference the User model once to be used in all tests
        cls.User = get_user_model()
        
        # Determine the base directory of the project to find test files
        cls.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Set up the path to the test file once for use in all test methods
        cls.test_file_path = os.path.join(cls.BASE_DIR, 'test_data', 'good_test_data.xlsx')

    def setUp(self):
        # This method is called before every individual test method to set up the endpoints, user createion, and login response data
        
        # Set up the URLs for different API endpoints that will be tested
        self.read_user_data_url = reverse('read_user_data')
        self.login_url = reverse('login')
        self.process_data_url = reverse('process_data')

        # Create a test user in the database for authentication purposes
        self.user = self.User.objects.create_user(username='testreaduserdata', email='testreaduserdata@test.com', password='testpass')

        # Log in the test user and save the access token for authenticating further requests
        login_response = self.client.post(self.login_url, {'email': 'testreaduserdata@test.com', 'password': 'testpass'}, format='json')
        self.access_token = login_response.data['access']

    def upload_test_file(self):
        # Helper method to upload a test file using the constructed path and saved access token
        
        # Read the content of the test file
        with open(self.test_file_path, 'rb') as real_file:
            file_content = real_file.read()

        # Wrap the file content in a SimpleUploadedFile to be sent via the test client
        file = SimpleUploadedFile(
            name="good_test_data.xlsx",
            content=file_content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Post the file to the processing endpoint with authentication
        self.client.post(self.process_data_url, {'file': file}, format='multipart', HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def check_response_code(self, response, expected_status_code):
        # Helper method to assert that the response code matches the expected status code
        
        # Assert that the response status code is as expected
        self.assertEqual(response.status_code, expected_status_code)

    # Test reading user data with valid credentials
    def test_read_user_data(self):
        # Upload the test data file
        self.upload_test_file()

        # Make the GET request to read user data with authentication
        response = self.client.get(self.read_user_data_url, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Check that the response status code is 200 OK
        self.check_response_code(response, status.HTTP_200_OK)

    # Test reading user data when no data has been uploaded yet
    def test_read_user_no_data(self):
        # Make the GET request to read user data without prior data upload
        response = self.client.get(self.read_user_data_url, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Check that the response status code is 404 Not Found since there's no data
        self.check_response_code(response, status.HTTP_404_NOT_FOUND)

    # Test reading user data with an invalid access token
    def test_read_user_data_invalid_access_token(self):
        # Upload the test data file.
        self.upload_test_file()
        
        # Modify the access token to make it invalid
        invalid_access_token = self.access_token.rsplit('.', 1)[0] + '.invalidsignature'
        
        # Make the GET request with the invalid token
        response = self.client.get(self.read_user_data_url, HTTP_AUTHORIZATION=f'Bearer {invalid_access_token}')
        
        # Check that the response status code is 401 Unauthorized due to the invalid token
        self.check_response_code(response, status.HTTP_401_UNAUTHORIZED)