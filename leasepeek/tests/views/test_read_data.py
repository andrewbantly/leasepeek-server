# Required libraries/modules for testing data read endpoint
import os
import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

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

        self.user_data_payload = {
            'email': 'testuserdataread@test.com',
            'password': 'testpass'
        }

        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.test_file_path = os.path.join(self.BASE_DIR, 'test_data', 'good_test_data.xlsx')

        with open(self.test_file_path, 'rb') as real_file:
            file_content = real_file.read()

        self.file = SimpleUploadedFile(
                name="good_test_data.xlsx",
                content=file_content,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # Test read data 
    def test_read_data(self):
        # An access token of a logged in user is required for the read data request
        login_response = self.client.post(self.login_url, self.user_data_payload, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access_token = login_response.data['access']

        # A objectId of a MongoDB document is required for the read data request
        test_file_path = os.path.join(self.BASE_DIR, 'test_data', 'good_test_data.xlsx')
        with open(test_file_path, 'rb') as real_file:
            file_content = real_file.read()
        file = SimpleUploadedFile(
                name="good_test_data.xlsx",
                content=file_content,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        data_upload_response = self.client.post(self.process_data_url, {'file': file}, format='multipart', HTTP_AUTHORIZATION=f'Bearer {access_token}')
        self.assertEqual(data_upload_response.status_code, status.HTTP_201_CREATED)
        response_data = json.loads(data_upload_response.content)
        objectId = response_data['objectId']

        # Send read data GET request with valid objectId and access token 
        data_read_response = self.client.get(self.read_data_url, {'objectId': objectId}, HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Check that the data read was successful
        self.assertEqual(data_read_response.status_code, status.HTTP_200_OK)

    # Test read data with invalid objectId
    def test_read_data_invalid_objectId(self):
        # An access token of a logged in user is required for the read data request
        login_response = self.client.post(self.login_url, self.user_data_payload, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access_token = login_response.data['access']

        # A objectId of a MongoDB document is required for the read data request
        objectId = "03544c995cef54d4495facb4"
        
        # Send read data GET request with valid objectId and access token 
        data_read_response = self.client.get(self.read_data_url, {'objectId': objectId}, HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Check that the data read was successful
        self.assertEqual(data_read_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_read_data_invalid_access_token(self):
        # A valid access token of a logged in user is required to add a MongoDB document object
        login_response = self.client.post(self.login_url, self.user_data_payload, format='json')
        access_token = login_response.data['access']

        # A objectId of a MongoDB document is required for the read data request
        test_file_path = os.path.join(self.BASE_DIR, 'test_data', 'good_test_data.xlsx')
        with open(test_file_path, 'rb') as real_file:
            file_content = real_file.read()
        file = SimpleUploadedFile(
                name="good_test_data.xlsx",
                content=file_content,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        data_upload_response = self.client.post(self.process_data_url, {'file': file}, format='multipart', HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response_data = json.loads(data_upload_response.content)
        objectId = response_data['objectId']

        # Modify the access token
        invalid_access_token = access_token.rsplit('.', 1)[0] + '.invalidsignature'

        # Send read data GET request with valid objectId and invalid access token 
        data_read_response = self.client.get(self.read_data_url, {'objectId': objectId}, HTTP_AUTHORIZATION=f'Bearer {invalid_access_token}')

        # Check that the data read was unauthorized
        self.assertEqual(data_read_response.status_code, status.HTTP_401_UNAUTHORIZED)