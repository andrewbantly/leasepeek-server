# Required libraries/modules for testing data process endpoint
import os
import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from leasepeek.mongo_models import data_collection

class ProcessDataViewTest(APITestCase):
    def setUp(self):
        # Establish required end points
        self.process_data_url = reverse('process_data')
        self.login_url = reverse('login')

        # Get the User model
        self.User = get_user_model()
  
        # create a user
        self.user = self.User.objects.create_user(username='testuserdataprocess', email='testuserdataprocess@test.com', password='testpass')

        # Log in the test user and save the access token for authenticating further requests
        login_response = self.client.post(self.login_url, {'email': 'testuserdataprocess@test.com', 'password': 'testpass'}, format='json')
        self.access_token = login_response.data['access']


    def upload_test_file(self, filename):
        # Helper method to prepare a test file for upload using the saved access token

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        test_file_path = os.path.join(BASE_DIR, 'test_data', filename)

        with open(test_file_path, 'rb') as real_file:
            file_content = real_file.read()

        file = SimpleUploadedFile(
                name=f"{filename}",
                content=file_content,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        return file

    # Test valid file upload with valid credentials
    def test_process_valid_data(self):
        # Test file names
        test_files = ['good_test_data.xlsx', 'private_test_data_01.xlsx','private_test_data_02.xlsx', 'private_test_data_03.xlsx', 'private_test_data_04.xlsx', 'private_test_data_05.xlsx', 'private_test_data_06.xlsx']

        for name in test_files:
            # Prepare the test file for upload
            file = self.upload_test_file(name)
    
            # Send process data POST request
            response = self.client.post(self.process_data_url, {'file': file}, format='multipart', HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

            # Check that the upload was successful
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            # JSON Response Data
            response_data = json.loads(response.content)

            # Ensure the response message is present in the response
            self.assertIn('message', response_data)
            self.assertEqual(response_data['message'], "Excel file processed successfully.")

            # Ensure the objectId is present in the response and formatted correctly 
            self.assertIn('objectId', response_data)
            self.assertRegex(response_data['objectId'], '^[a-f0-9]{24}$')

    # Test invalid file type upload with valid credentials 
    def test_invalid_file_type(self):
        # Prepare the test file for upload
        file = self.upload_test_file('csv_test_data.csv')
    
        # Send process data POST request with invalid file type
        response = self.client.post(self.process_data_url, {'file': file}, format='multipart', HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Ensure the file upload response returns a 400 status code indicating a bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # Test no file upload with valid credentials
    def test_no_file(self):
        # Send process data POST request with invalid file type
        response = self.client.post(self.process_data_url, {}, format='multipart', HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Ensure the file upload response returns a 400 status code indicating bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    # Tear down function to clean data from the test MongoDB
    def tearDown(self):
        # Delete all documents in the dat collection
        try:
            data_collection.delete_many({})
        except Exception as e:
            print(f"An error occurred during teardown: {e}")