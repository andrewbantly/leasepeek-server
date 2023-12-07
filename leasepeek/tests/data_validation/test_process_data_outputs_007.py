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
        file_name = os.environ.get('07_TEST_FILE_NAME')
        objectId = self.upload_test_file(file_name)
        response = self.client.get(self.read_data_url, {'objectId': objectId}, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response_data = json.loads(response.content)[0]


        self.assertEqual(response_data['asOf'], os.environ.get('07_TEST_FILE_AS_OF'))
        self.assertEqual(response_data['location']['building'], os.environ.get('07_TEST_FILE_LOCATION'))
        self.assertEqual(response_data['totalUnits'], 176)
        self.assertEqual(response_data['totalBalance'], -21900.57)
        self.assertEqual(response_data['vacancy']['Occupied'], 161)
        self.assertEqual(response_data['vacancy']['Vacant'], 15)
    
        self.assertEqual(response_data['lossToLease']['marketSum'], 329654)
        self.assertEqual(response_data['lossToLease']['rentIncome'], 285941)
        # Floor plan analysis testing
        days_90 = 'last_90_days'
        days_60 = 'last_60_days'
        days_30 = 'last_30_days'
        expiring_90 = "expiring_in_90_days"
        expired = "expired"

        floorplan1 = os.environ.get('07_TEST_FILE_FLOORPLAN_1')
        self.assertEqual(response_data['floorplans'][floorplan1]['avgRent'], 1790.94)
        self.assertEqual(response_data['floorplans'][floorplan1]['sumRent'], 91338)
        self.assertEqual(response_data['floorplans'][floorplan1]['avgMarket'], 1859.52)
        self.assertEqual(response_data['floorplans'][floorplan1]['sumMarket'], 96695)
        self.assertEqual(response_data['floorplans'][floorplan1]['unitCount'], 52)
        self.assertEqual(response_data['floorplans'][floorplan1]['avgSqft'], 1172.0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_two']['total_rent'], 3636)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_two']['average_rent'], 1818.0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_90]['count'], 3)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_90]['total_rent'], 5521)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_90]['average_rent'], 1840.33)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_60]['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_60]['total_rent'], 3636)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_60]['average_rent'], 1818.0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_30]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_30]['total_rent'], 1898)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_30]['average_rent'], 1898.0)
        self.assertEqual(response_data['expiringLeases'][floorplan1][expiring_90]['count'], 11)
        self.assertEqual(response_data['expiringLeases'][floorplan1][expiring_90]['total_rent'], 20011)
        self.assertEqual(response_data['expiringLeases'][floorplan1][expired]['count'], 1)
        self.assertEqual(response_data['expiringLeases'][floorplan1][expired]['total_rent'], 1975)

        floorplan2 = os.environ.get('07_TEST_FILE_FLOORPLAN_2')
        self.assertEqual(response_data['floorplans'][floorplan2]['avgRent'], 1782.32)
        self.assertEqual(response_data['floorplans'][floorplan2]['sumRent'], 33864)
        self.assertEqual(response_data['floorplans'][floorplan2]['avgMarket'], 1844.77)
        self.assertEqual(response_data['floorplans'][floorplan2]['sumMarket'], 40585)
        self.assertEqual(response_data['floorplans'][floorplan2]['unitCount'], 22)
        self.assertEqual(response_data['floorplans'][floorplan2]['avgSqft'], 1130.0)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_two']['total_rent'], 3519)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_two']['average_rent'], 1759.5)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_90]['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_90]['total_rent'], 3519)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_90]['average_rent'], 1759.5)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_60]['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_60]['total_rent'], 3519)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_60]['average_rent'], 1759.5)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_30]['average_rent'], 0)
        self.assertEqual(response_data['expiringLeases'][floorplan2][expiring_90]['count'], 7)
        self.assertEqual(response_data['expiringLeases'][floorplan2][expiring_90]['total_rent'], 12499)
        self.assertEqual(response_data['expiringLeases'][floorplan2][expired]['count'], 0)
        self.assertEqual(response_data['expiringLeases'][floorplan2][expired]['total_rent'], 0)


        floorplan3 = os.environ.get('07_TEST_FILE_FLOORPLAN_3')
        self.assertEqual(response_data['floorplans'][floorplan3]['avgRent'], 1548.33)
        self.assertEqual(response_data['floorplans'][floorplan3]['sumRent'], 9290)
        self.assertEqual(response_data['floorplans'][floorplan3]['avgMarket'], 1739.86)
        self.assertEqual(response_data['floorplans'][floorplan3]['sumMarket'], 12179)
        self.assertEqual(response_data['floorplans'][floorplan3]['unitCount'], 7)
        self.assertEqual(response_data['floorplans'][floorplan3]['avgSqft'], 833.0)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_two']['total_rent'], 3193)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_two']['average_rent'], 1596.5)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_90]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_90]['total_rent'], 1518)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_90]['average_rent'], 1518.0)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_60]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_30]['average_rent'], 0)
        self.assertEqual(response_data['expiringLeases'][floorplan3][expiring_90]['count'], 0)
        self.assertEqual(response_data['expiringLeases'][floorplan3][expiring_90]['total_rent'], 0)
        self.assertEqual(response_data['expiringLeases'][floorplan3][expired]['count'], 0)
        self.assertEqual(response_data['expiringLeases'][floorplan3][expired]['total_rent'], 0)





    # Tear down function to clean data from the test MongoDB
    def tearDown(self):
        # Delete all documents in the dat collection
        try:
            data_collection.delete_many({})
        except Exception as e:
            print(f"An error occurred during teardown: {e}")