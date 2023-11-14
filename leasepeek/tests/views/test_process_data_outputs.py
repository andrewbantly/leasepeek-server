import os
import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from leasepeek.mongo_models import data_collection

class ProcessDataViewValuesTest(APITestCase):
    def setUp(self):
        # Establish required end points
        self.process_data_url = reverse('process_data')
        self.login_url = reverse('login')
        self.read_data_url = reverse('read_data')

        # Get the User model
        self.User = get_user_model()
  
        # create a user
        self.user = self.User.objects.create_user(username='testuserdataprocessvalues', email='testuserdataprocessvalues@test.com', password='testpass')

        # Log in the test user and save the access token for authenticating further requests
        login_response = self.client.post(self.login_url, {'email': 'testuserdataprocessvalues@test.com', 'password': 'testpass'}, format='json')
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
        
                # Post the file to the processing endpoint with authentication
        
        response = self.client.post(self.process_data_url, {'file': file}, format='multipart', HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response_data = json.loads(response.content)
        objectId = response_data['objectId']

        return objectId
    
    # Test valid file upload with valid credentials
    def test_data_output_01(self):
        file_name = os.environ.get('01_TEST_FILE_NAME')
        objectId = self.upload_test_file(file_name)
        response = self.client.get(self.read_data_url, {'objectId': objectId}, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response_data = json.loads(response.content)[0]

        print(response_data)

        self.assertEqual(response_data['asOf'], os.environ.get('01_TEST_FILE_AS_OF'))
        self.assertEqual(response_data['location'], os.environ.get('01_TEST_FILE_LOCATION'))
        self.assertEqual(response_data['totalUnits'], 15)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_01')]['avgRent'], 661.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_01')]['sumRent'], 661)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_01')]['avgMarket'], 750.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_01')]['sumMarket'], 2250)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_01')]['unitCount'], 3)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_01')]['avgSqft'], 600.0)
