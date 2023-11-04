# Required libraries/modules for testing data read endpoint
import os
import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from leasepeek.mongo_models import data_collection

class ReadDataViewTest(APITestCase):
    def setUp(self):
        # Establish required end points
        self.login_url = reverse('login')
        self.process_data_url = reverse('process_data')
        self.read_data_url = reverse('read_data')
    
        # Get the User model
        self.User = get_user_model()

        # Create a User
        self.user = self.User.objects.create_user(username='testuserdataread', email='testuserdataread@test.com', password='testpass')

        # Log in the test user and save the access token for authenticating further requests
        login_response = self.client.post(self.login_url, {'email': 'testuserdataread@test.com', 'password': 'testpass'}, format='json')
        self.access_token = login_response.data['access']


    def upload_test_file(self, filename):
        # Helper method to upload a test file using the saved access token

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        test_file_path = os.path.join(BASE_DIR, 'test_data', filename)

        with open(test_file_path, 'rb') as real_file:
            file_content = real_file.read()

        file = SimpleUploadedFile(
                name=f"{filename}",
                content=file_content,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        # Post the file to the processing endpoint with authentication
        response = self.client.post(self.process_data_url, {'file': file}, format='multipart', HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response_data = json.loads(response.content)
        objectId = response_data['objectId']

        return objectId

    # Test read data
    def test_read_data(self):     
        # Upload the test file
        objectId = self.upload_test_file('good_test_data.xlsx')

        # Send read data GET request with valid objectId and access token 
        response = self.client.get(self.read_data_url, {'objectId': objectId}, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Check that the data read was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Test read data with invalid objectId
    def test_read_data_invalid_objectId(self):
        # A objectId of a MongoDB document is required for the read data request
        objectId = "03544c995cef54d4495facb4"
        
        # Send read data GET request with valid objectId and access token 
        response = self.client.get(self.read_data_url, {'objectId': objectId}, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Check that the data read was unsuccessful
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # Test read data with invalid access token
    def test_read_data_invalid_access_token(self):
        # Upload the test file
        objectId = self.upload_test_file('good_test_data.xlsx')

        # Modify the access token
        invalid_access_token = self.access_token.rsplit('.', 1)[0] + '.invalidsignature'

        # Send read data GET request with valid objectId and invalid access token 
        data_read_response = self.client.get(self.read_data_url, {'objectId': objectId}, HTTP_AUTHORIZATION=f'Bearer {invalid_access_token}')

        # Check that the data read was unauthorized
        self.assertEqual(data_read_response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    # Tear down function to clean data from the test MongoDB
    def tearDown(self):
        # Delete all documents in the dat collection
        try:
            data_collection.delete_many({})
        except Exception as e:
            print(f"An error occurred during teardown: {e}")