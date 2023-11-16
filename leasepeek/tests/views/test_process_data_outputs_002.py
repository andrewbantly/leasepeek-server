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
        file_name = os.environ.get('02_TEST_FILE_NAME')
        objectId = self.upload_test_file(file_name)
        response = self.client.get(self.read_data_url, {'objectId': objectId}, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response_data = json.loads(response.content)[0]

        self.assertEqual(response_data['asOf'], os.environ.get('02_TEST_FILE_AS_OF'))
        self.assertEqual(response_data['location'], os.environ.get('02_TEST_FILE_LOCATION'))
        self.assertEqual(response_data['totalUnits'], 300)

        self.assertEqual(response_data['vacancy']['Occupied'], 276)
        self.assertEqual(response_data['vacancy']['Vacant'], 24)
       
        self.assertEqual(response_data['lossToLease']['marketSum'], 504484)
        self.assertEqual(response_data['lossToLease']['rentIncome'], 407398)

        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_0')]['avgRent'], 0.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_0')]['sumRent'], 0)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_0')]['avgMarket'], 1797.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_0')]['sumMarket'], 1797)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_0')]['unitCount'], 1)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_0')]['avgSqft'], 1015.0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_0')]['recent_two'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_0')]['recent_leases']['last_90_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_0')]['recent_leases']['last_60_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_0')]['recent_leases']['last_30_days'], 0) 

        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_1')]['avgRent'], 1439.5)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_1')]['sumRent'], 17274)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_1')]['avgMarket'], 1710.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_1')]['sumMarket'], 22230)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_1')]['unitCount'], 13)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_1')]['avgSqft'], 1009.0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_1')]['recent_two'], 2)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_1')]['recent_leases']['last_90_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_1')]['recent_leases']['last_60_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_1')]['recent_leases']['last_30_days'], 0) 

        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_2')]['avgRent'], 1510.73)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_2')]['sumRent'], 16618)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_2')]['avgMarket'], 1715.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_2')]['sumMarket'], 20580)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_2')]['unitCount'], 12)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_2')]['avgSqft'], 1009.0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_2')]['recent_two'], 2)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_2')]['recent_leases']['last_90_days'], 1)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_2')]['recent_leases']['last_60_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_2')]['recent_leases']['last_30_days'], 0) 

        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_3')]['avgRent'], 1526.46)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_3')]['sumRent'], 19844)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_3')]['avgMarket'], 1705.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_3')]['sumMarket'], 23870)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_3')]['unitCount'], 14)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_3')]['avgSqft'], 1015.0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_3')]['recent_two'], 2)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_3')]['recent_leases']['last_90_days'], 3)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_3')]['recent_leases']['last_60_days'], 2)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_3')]['recent_leases']['last_30_days'], 1) 

        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_4')]['avgRent'], 1485.73)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_4')]['sumRent'], 16343)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_4')]['avgMarket'], 1710.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_4')]['sumMarket'], 20520)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_4')]['unitCount'], 12)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_4')]['avgSqft'], 1015.0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_4')]['recent_two'], 2)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_4')]['recent_leases']['last_90_days'], 2)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_4')]['recent_leases']['last_60_days'], 2)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_4')]['recent_leases']['last_30_days'], 0) 

        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_5')]['avgRent'], 1537.62)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_5')]['sumRent'], 19989)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_5')]['avgMarket'], 1735.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_5')]['sumMarket'], 24290)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_5')]['unitCount'], 14)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_5')]['avgSqft'], 1015.0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_5')]['recent_two'], 2)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_5')]['recent_leases']['last_90_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_5')]['recent_leases']['last_60_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_5')]['recent_leases']['last_30_days'], 0) 

        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_6')]['avgRent'], 1511.2)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_6')]['sumRent'], 15112)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_6')]['avgMarket'], 1740.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_6')]['sumMarket'], 19140)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_6')]['unitCount'], 11)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_6')]['avgSqft'], 1015.0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_6')]['recent_two'], 2)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_6')]['recent_leases']['last_90_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_6')]['recent_leases']['last_60_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_6')]['recent_leases']['last_30_days'], 0) 

        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_7')]['avgRent'], 1739.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_7')]['sumRent'], 1739)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_7')]['avgMarket'], 1950.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_7')]['sumMarket'], 1950)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_7')]['unitCount'], 1)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_7')]['avgSqft'], 1132.0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_7')]['recent_two'], 1)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_7')]['recent_leases']['last_90_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_7')]['recent_leases']['last_60_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_7')]['recent_leases']['last_30_days'], 0) 

        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_8')]['avgRent'], 1740.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_8')]['sumRent'], 8700)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_8')]['avgMarket'], 1955.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_8')]['sumMarket'], 9775)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_8')]['unitCount'], 5)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_8')]['avgSqft'], 1132.0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_8')]['recent_two'], 2)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_8')]['recent_leases']['last_90_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_8')]['recent_leases']['last_60_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_8')]['recent_leases']['last_30_days'], 0) 

        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_9')]['avgRent'], 1766.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_9')]['sumRent'], 8830)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_9')]['avgMarket'], 1950.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_9')]['sumMarket'], 13650)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_9')]['unitCount'], 7)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_9')]['avgSqft'], 1132.0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_8')]['recent_two'], 2)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_8')]['recent_leases']['last_90_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_8')]['recent_leases']['last_60_days'], 0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_8')]['recent_leases']['last_30_days'], 0) 

        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_10')]['avgRent'], 1759.86)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_10')]['sumRent'], 12319)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_10')]['avgMarket'], 1945.0)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_10')]['sumMarket'], 15560)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_10')]['unitCount'], 8)
        self.assertEqual(response_data['floorplans'][os.environ.get('02_TEST_FILE_FLOORPLAN_10')]['avgSqft'], 1132.0)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_10')]['recent_two'], 2)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_10')]['recent_leases']['last_90_days'], 2)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_10')]['recent_leases']['last_60_days'], 1)
        self.assertEqual(response_data['recentLeases'][os.environ.get('02_TEST_FILE_FLOORPLAN_10')]['recent_leases']['last_30_days'], 0) 

        
    # Tear down function to clean data from the test MongoDB
    def tearDown(self):
        # Delete all documents in the dat collection
        try:
            data_collection.delete_many({})
        except Exception as e:
            print(f"An error occurred during teardown: {e}")