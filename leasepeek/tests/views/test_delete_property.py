# Required imports for testing Delete Property endpoint
import os
import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from leasepeek.mongo_models import data_collection

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
        self.delete_property_url = reverse('delete_property')
        self.login_url = reverse('login')
        self.process_data_url = reverse('process_data')

        # Create a test user in the database for authentication purposes
        self.user = self.User.objects.create_user(username='testproperty', email='testproperty@test.com', password='testpass')

        # Log in the test user and save the access token for authenticating further requests
        login_response = self.client.post(self.login_url, {'email': 'testproperty@test.com', 'password': 'testpass'}, format='json')
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

        # Post the file to the processing endpoint with authentication and retrieve objectId
        data_response = self.client.post(self.process_data_url, {'file': file}, format='multipart', HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response_data = json.loads(data_response.content)
        self.objectId = response_data['objectId']

    
    def check_response_code(self, response, expected_status_code):
        # Helper method to assert that the response code matches the expected status code
        
        # Assert that the response status code is as expected
        self.assertEqual(response.status_code, expected_status_code)

    # Test delete property with valid credentials
    def test_delete_property(self):
        # Upload the test data file
        self.upload_test_file()

        # Construct the URL with the objectId as a query parameter
        url_with_objectId = f"{self.delete_property_url}?objectId={self.objectId}"

        # Make the DELETE request to delete property endpoint with authentication
        response = self.client.delete(url_with_objectId, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
         # Check that the response status code is 200 OK
        self.check_response_code(response, status.HTTP_200_OK)

    # Test delete property with invalid credentials
    def test_delete_property_invalid_credentials(self):
        # Assume the setup has created an objectId
        self.upload_test_file()

        # Make the DELETE request without the necessary authentication header
        url_with_objectId = f"{self.delete_property_url}?objectId={self.objectId}"
        response = self.client.delete(url_with_objectId)

        # Check that the response status code is 401 unauthorized
        self.check_response_code(response, status.HTTP_401_UNAUTHORIZED)

    # Test delete property with nonexistent objectId
    def test_delete_property_nonexistent_objectId(self):
        # Construct a fake objectId
        fake_objectId = '5e9f8f8f8f8f8f8f8f8f8f8f'

        # Make the DELETE request with the fake objectId
        url_with_fake_objectId = f"{self.delete_property_url}?objectId={fake_objectId}"
        response = self.client.delete(url_with_fake_objectId, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Check that the response status code is 404 not found
        self.check_response_code(response, status.HTTP_404_NOT_FOUND)

    # Test delete property with invalid objectId format
    def test_delete_property_invalid_objectId_format(self):
        # Construct an invalid objectId
        invalid_objectId = 'invalid-object-id'

        # Make the DELETE request with the invalid objectId
        url_with_invalid_objectId = f"{self.delete_property_url}?objectId={invalid_objectId}"
        response = self.client.delete(url_with_invalid_objectId, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Check that the response status code is 400 BAD REQUEST
        self.check_response_code(response, status.HTTP_400_BAD_REQUEST)

    # Test delete property with no objectId provided
    def test_delete_property_no_objectId(self):
        # Make the DELETE request without objectId
        response = self.client.delete(self.delete_property_url, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Check that the response status code is 400 BAD REQUEST
        self.check_response_code(response, status.HTTP_400_BAD_REQUEST)
    
    # Tear down function to clean data from the test MongoDB
    def tearDown(self):
        # Delete all documents in the dat collection
        try:
            data_collection.delete_many({})
        except Exception as e:
            print(f"An error occurred during teardown: {e}")

