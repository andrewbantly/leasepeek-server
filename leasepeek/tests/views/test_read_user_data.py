# # Required libraries/modules for testing read user data endpoint
import os
import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

class ReadUserDataViewTest(APITestCase):
    def setUp(self):
        # Establish required end points
        self.read_user_data_url = reverse('read_user_data')
        self.login_url = reverse('login')
        self.process_data_url = reverse('process_data')

        # Get the User model
        self.User = get_user_model()

        # Create a user
        self.user = self.User.objects.create_user(username='testreaduserdata', email='testreaduserdata@test.com', password='testpass')

        # Login the user to get the access token in order to create a data upload
        self.user_data_payload = {
            'email': 'testreaduserdata@test.com',
            'password': 'testpass'
        }
        login_response = self.client.post(self.login_url, self.user_data_payload, format='json')
        self.access_token = login_response.data['access']


        # Construct the path to the test file
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_file_path = os.path.join(BASE_DIR, 'test_data', 'good_test_data.xlsx')

        # Open the file and read its content in binary mode
        with open(test_file_path, 'rb') as real_file:
            file_content = real_file.read()

        # Create a SimpleUploadedFile with content read from the real file
        file = SimpleUploadedFile(
                name="good_test_data.xlsx",
                content=file_content,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        # Send process data POST request
        data_upload_response = self.client.post(self.process_data_url, {'file': file}, format='multipart', HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Check that the upload was successful
        self.assertEqual(data_upload_response.status_code, status.HTTP_201_CREATED)


    # Test read user data with valid credentials
    def test_read_user_data(self):
        response = self.client.get(self.read_user_data_url, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)


