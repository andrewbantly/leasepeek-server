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

        self.user_data_payload = {
            'email': 'testuserdataprocess@test.com',
            'password': 'testpass'
        }

        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Test valid file upload with valid credentials
    def test_process_valid_data(self):
        # User needs to be logged in
        login_response = self.client.post(self.login_url, self.user_data_payload, format='json')

        # Ensure the login response returns a 200 status code indicating login successful
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Get the Access token from the response data
        access_token = login_response.data['access']

        # Construct the path to the test file
        test_file_path = os.path.join(self.BASE_DIR, 'test_data', 'good_test_data.xlsx')

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
        response = self.client.post(self.process_data_url, {'file': file}, format='multipart', HTTP_AUTHORIZATION=f'Bearer {access_token}')

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
        # User needs to be logged in
        login_response = self.client.post(self.login_url, self.user_data_payload, format='json')

        # Ensure the login response returns a 200 status code indicating login successful
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Get the Access token from the response data
        access_token = login_response.data['access']
    
        # Construct the path to the invalid test file
        test_file_path = os.path.join(self.BASE_DIR, 'test_data', 'csv_test_data.csv')

        # Open the file and read its content in binary mode
        with open(test_file_path, 'rb') as real_file:
            file_content = real_file.read()
    
        # Create a SimpleUploadFile with content read from the read file
        file = SimpleUploadedFile(
            name="invalid_test_file",
            content=file_content,
            content_type="text/csv"
        )
    
        # Send process data POST request with invalid file type
        response = self.client.post(self.process_data_url, {'file': file}, format='multipart', HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Ensure the file upload response returns a 400 status code indicating a bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # Test no file upload with valid credentials
    def test_no_file(self):
        # User needs to be logged in
        login_response = self.client.post(self.login_url, self.user_data_payload, format='json')

        # Ensure the login response returns a 200 status code indicating login successful
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Get the Access token from the response data
        access_token = login_response.data['access']

        # Send process data POST request with invalid file type
        response = self.client.post(self.process_data_url, {}, format='multipart', HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Ensure the file upload response returns a 400 status code indicating bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    # Tear down function to clean data from the test MongoDB
    def tearDown(self):
        # Delete all documents in the dat collection
        try:
            data_collection.delete_many({})
        except Exception as e:
            print(f"An error occurred during teardown: {e}")