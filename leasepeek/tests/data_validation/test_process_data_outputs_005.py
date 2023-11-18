import os
import json
from django.urls import reverse
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
    def test_data_output(self):
        file_name = os.environ.get('05_TEST_FILE_NAME')
        objectId = self.upload_test_file(file_name)
        response = self.client.get(self.read_data_url, {'objectId': objectId}, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response_data = json.loads(response.content)[0]


        self.assertEqual(response_data['asOf'], os.environ.get('05_TEST_FILE_AS_OF'))
        self.assertEqual(response_data['location'], os.environ.get('05_TEST_FILE_LOCATION'))
        self.assertEqual(response_data['totalUnits'], 310)
        self.assertEqual(response_data['vacancy']['Occupied'], 262)
        self.assertEqual(response_data['vacancy']['Vacant'], 46)
        self.assertEqual(response_data['vacancy']['Model'], 2)
       
        self.assertEqual(response_data['lossToLease']['marketSum'], 542451)
        self.assertEqual(response_data['lossToLease']['rentIncome'], 461333)

        # Floor plan analysis testing
        # days_90 = 'last_90_days'
        # days_60 = 'last_60_days'
        # days_30 = 'last_30_days'

        # floorplan01 = os.environ.get('05_TEST_FILE_FLOORPLAN_01')
        # self.assertEqual(response_data['floorplans'][floorplan01]['avgRent'], 1364.5)
        # self.assertEqual(response_data['floorplans'][floorplan01]['sumRent'], 27290)
        # self.assertEqual(response_data['floorplans'][floorplan01]['avgMarket'], 1500.0)
        # self.assertEqual(response_data['floorplans'][floorplan01]['sumMarket'], 31500)
        # self.assertEqual(response_data['floorplans'][floorplan01]['unitCount'], 21)
        # self.assertEqual(response_data['floorplans'][floorplan01]['avgSqft'], 657.0)
        # self.assertEqual(response_data['recentLeases'][floorplan01]['recent_two']['count'], 2)
        # self.assertEqual(response_data['recentLeases'][floorplan01]['recent_two']['total_rent'], 2800)
        # self.assertEqual(response_data['recentLeases'][floorplan01]['recent_two']['average_rent'], 1400.0)
        # self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_90]['count'], 4)
        # self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_90]['total_rent'], 5500)
        # self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_90]['average_rent'], 1375.0)
        # self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_60]['count'], 1)
        # self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_60]['total_rent'], 1450)
        # self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_60]['average_rent'], 1450.0)
        # self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_30]['count'], 0)
        # self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_30]['total_rent'], 0)
        # self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_30]['average_rent'], 0)

    # Tear down function to clean data from the test MongoDB
    def tearDown(self):
        # Delete all documents in the dat collection
        try:
            data_collection.delete_many({})
        except Exception as e:
            print(f"An error occurred during teardown: {e}")