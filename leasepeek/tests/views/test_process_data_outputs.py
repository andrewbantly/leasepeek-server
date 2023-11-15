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

        self.assertEqual(response_data['asOf'], os.environ.get('01_TEST_FILE_AS_OF'))
        self.assertEqual(response_data['location'], os.environ.get('01_TEST_FILE_LOCATION'))
        self.assertEqual(response_data['totalUnits'], 15)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_01')]['avgRent'], 661.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_01')]['sumRent'], 661)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_01')]['avgMarket'], 750.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_01')]['sumMarket'], 2250)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_01')]['unitCount'], 3)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_01')]['avgSqft'], 600.0)

        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_02')]['avgRent'], 830.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_02')]['sumRent'], 830)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_02')]['avgMarket'], 875.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_02')]['sumMarket'], 875)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_02')]['unitCount'], 1)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_02')]['avgSqft'], 850.0)

        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_03')]['avgRent'], 1595.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_03')]['sumRent'], 3190)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_03')]['avgMarket'], 1495.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_03')]['sumMarket'], 4485)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_03')]['unitCount'], 3)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_03')]['avgSqft'], 750.0)

        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_04')]['avgRent'], 1595.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_04')]['sumRent'], 1595)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_04')]['avgMarket'], 1595.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_04')]['sumMarket'], 1595)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_04')]['unitCount'], 1)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_04')]['avgSqft'], 750.0)

        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_05')]['avgRent'], 0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_05')]['sumRent'], 0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_05')]['avgMarket'], 1620.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_05')]['sumMarket'], 3240)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_05')]['unitCount'], 2)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_05')]['avgSqft'], 750.0)

        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_06')]['avgRent'], 0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_06')]['sumRent'], 0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_06')]['avgMarket'], 1545.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_06')]['sumMarket'], 1545)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_06')]['unitCount'], 1)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_06')]['avgSqft'], 750.0)

        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_07')]['avgRent'], 0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_07')]['sumRent'], 0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_07')]['avgMarket'], 1645.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_07')]['sumMarket'], 3290)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_07')]['unitCount'], 2)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_07')]['avgSqft'], 750.0)

        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_08')]['avgRent'], 0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_08')]['sumRent'], 0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_08')]['avgMarket'], 1545.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_08')]['sumMarket'], 1545)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_08')]['unitCount'], 1)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_08')]['avgSqft'], 850.0)

        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_09')]['avgRent'], 0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_09')]['sumRent'], 0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_09')]['avgMarket'], 1545.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_09')]['sumMarket'], 1545)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_09')]['unitCount'], 1)
        self.assertEqual(response_data['floorplans'][os.environ.get('01_TEST_FILE_FLOORPLAN_09')]['avgSqft'], 850.0)

        self.assertEqual(response_data['vacancy']['occupied'], 6)
        self.assertEqual(response_data['vacancy']['vacant'], 9)
        self.assertEqual(response_data['vacancy']['upcoming'], 4)
       
        self.assertEqual(response_data['lossToLease']['marketSum'], 20370)
        self.assertEqual(response_data['lossToLease']['rentIncome'], 6276)

        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_01')]['recent_two'], 2)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_01')]['recent_leases']['last_90_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_01')]['recent_leases']['last_60_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_01')]['recent_leases']['last_30_days'], 0)

        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_02')]['recent_two'], 1)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_02')]['recent_leases']['last_90_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_02')]['recent_leases']['last_60_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_02')]['recent_leases']['last_30_days'], 0)

        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_03')]['recent_two'], 2)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_03')]['recent_leases']['last_90_days'], 2)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_03')]['recent_leases']['last_60_days'], 1)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_03')]['recent_leases']['last_30_days'], 0)
        
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_04')]['recent_two'], 1)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_04')]['recent_leases']['last_90_days'], 1)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_04')]['recent_leases']['last_60_days'], 1)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_04')]['recent_leases']['last_30_days'], 1)

        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_05')]['recent_two'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_05')]['recent_leases']['last_90_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_05')]['recent_leases']['last_60_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_05')]['recent_leases']['last_30_days'], 0)

        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_06')]['recent_two'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_06')]['recent_leases']['last_90_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_06')]['recent_leases']['last_60_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_06')]['recent_leases']['last_30_days'], 0)

        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_07')]['recent_two'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_07')]['recent_leases']['last_90_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_07')]['recent_leases']['last_60_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_07')]['recent_leases']['last_30_days'], 0)

        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_08')]['recent_two'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_08')]['recent_leases']['last_90_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_08')]['recent_leases']['last_60_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_08')]['recent_leases']['last_30_days'], 0)

        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_08')]['recent_two'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_08')]['recent_leases']['last_90_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_08')]['recent_leases']['last_60_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('01_TEST_FILE_FLOORPLAN_08')]['recent_leases']['last_30_days'], 0)

    def test_data_output_04(self):
        file_name = os.environ.get('04_TEST_FILE_NAME')
        objectId = self.upload_test_file(file_name)
        response = self.client.get(self.read_data_url, {'objectId': objectId}, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response_data = json.loads(response.content)[0]

        self.assertEqual(response_data['asOf'], os.environ.get('04_TEST_FILE_AS_OF'))
        self.assertEqual(response_data['location'], os.environ.get('04_TEST_FILE_LOCATION'))
        self.assertEqual(response_data['totalUnits'], 324)