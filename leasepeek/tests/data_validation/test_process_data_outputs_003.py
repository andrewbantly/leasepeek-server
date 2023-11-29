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
        file_name = os.environ.get('03_TEST_FILE_NAME')
        objectId = self.upload_test_file(file_name)
        response = self.client.get(self.read_data_url, {'objectId': objectId}, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response_data = json.loads(response.content)[0]
        days_90 = 'last_90_days'
        days_60 = 'last_60_days'
        days_30 = 'last_30_days'

        self.assertEqual(response_data['asOf'], os.environ.get('02_TEST_FILE_AS_OF'))
        self.assertEqual(response_data['location'], os.environ.get('02_TEST_FILE_LOCATION'))
        self.assertEqual(response_data['totalUnits'], 300)
        self.assertEqual(response_data['totalBalance'], -2838.75)

        self.assertEqual(response_data['vacancy']['Occupied'], 275)
        self.assertEqual(response_data['vacancy']['Vacant'], 24)
        self.assertEqual(response_data['vacancy']['Model'], 1)
       
        self.assertEqual(response_data['lossToLease']['marketSum'], 504484)
        self.assertEqual(response_data['lossToLease']['rentIncome'], 405967)

        floorplan1 = os.environ.get('03_TEST_FILE_FLOORPLAN_1')
        self.assertEqual(response_data['floorplans'][floorplan1]['avgRent'], 0.0)
        self.assertEqual(response_data['floorplans'][floorplan1]['sumRent'], 0)
        self.assertEqual(response_data['floorplans'][floorplan1]['avgMarket'], 1797.0)
        self.assertEqual(response_data['floorplans'][floorplan1]['sumMarket'], 1797)
        self.assertEqual(response_data['floorplans'][floorplan1]['unitCount'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_two']['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_two']['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_two']['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_90]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_60]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_30]['average_rent'], 0)

        floorplan2 = os.environ.get('03_TEST_FILE_FLOORPLAN_2')
        self.assertEqual(response_data['floorplans'][floorplan2]['avgRent'], 1440.27)
        self.assertEqual(response_data['floorplans'][floorplan2]['sumRent'], 15843)
        self.assertEqual(response_data['floorplans'][floorplan2]['avgMarket'], 1710.0)
        self.assertEqual(response_data['floorplans'][floorplan2]['sumMarket'], 22230)
        self.assertEqual(response_data['floorplans'][floorplan2]['unitCount'], 13)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_two']['total_rent'], 2946)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_two']['average_rent'], 1473)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_90]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_60]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_30]['average_rent'], 0)

        floorplan3 = os.environ.get('03_TEST_FILE_FLOORPLAN_3')
        self.assertEqual(response_data['floorplans'][floorplan3]['avgRent'], 1510.73)
        self.assertEqual(response_data['floorplans'][floorplan3]['sumRent'], 16618)
        self.assertEqual(response_data['floorplans'][floorplan3]['avgMarket'], 1715.0)
        self.assertEqual(response_data['floorplans'][floorplan3]['sumMarket'], 20580)
        self.assertEqual(response_data['floorplans'][floorplan3]['unitCount'], 12)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_two']['total_rent'], 3100)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_two']['average_rent'], 1550)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_90]['count'], 3)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_90]['total_rent'], 4560)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_90]['average_rent'], 1520)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_60]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_60]['total_rent'], 1650)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_60]['average_rent'], 1650)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_30]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_30]['total_rent'], 1650)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_30]['average_rent'], 1650)

        floorplan4 = os.environ.get('03_TEST_FILE_FLOORPLAN_4')
        self.assertEqual(response_data['floorplans'][floorplan4]['avgRent'], 1526.46)
        self.assertEqual(response_data['floorplans'][floorplan4]['sumRent'], 19844)
        self.assertEqual(response_data['floorplans'][floorplan4]['avgMarket'], 1705.0)
        self.assertEqual(response_data['floorplans'][floorplan4]['sumMarket'], 23870)
        self.assertEqual(response_data['floorplans'][floorplan4]['unitCount'], 14)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_two']['total_rent'], 3255)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_two']['average_rent'], 1627.5)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_90]['count'], 5)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_90]['total_rent'], 7896)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_90]['average_rent'], 1579.2)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_60]['count'], 4)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_60]['total_rent'], 6339)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_60]['average_rent'], 1584.75)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_30]['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_30]['total_rent'], 3255)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_30]['average_rent'], 1627.5)
    
        floorplan5 = os.environ.get('03_TEST_FILE_FLOORPLAN_5')
        self.assertEqual(response_data['floorplans'][floorplan5]['avgRent'], 1485.73)
        self.assertEqual(response_data['floorplans'][floorplan5]['sumRent'], 16343)
        self.assertEqual(response_data['floorplans'][floorplan5]['avgMarket'], 1710.0)
        self.assertEqual(response_data['floorplans'][floorplan5]['sumMarket'], 20520)
        self.assertEqual(response_data['floorplans'][floorplan5]['unitCount'], 12)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_two']['total_rent'], 3065)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_two']['average_rent'], 1532.5)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_90]['count'], 3)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_90]['total_rent'], 4590)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_90]['average_rent'], 1530.0)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_60]['count'], 3)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_60]['total_rent'], 4590)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_60]['average_rent'], 1530.0)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_30]['average_rent'], 0)
    
        floorplan6 = os.environ.get('03_TEST_FILE_FLOORPLAN_6')
        self.assertEqual(response_data['floorplans'][floorplan6]['avgRent'], 1537.62)
        self.assertEqual(response_data['floorplans'][floorplan6]['sumRent'], 19989)
        self.assertEqual(response_data['floorplans'][floorplan6]['avgMarket'], 1735.0)
        self.assertEqual(response_data['floorplans'][floorplan6]['sumMarket'], 24290)
        self.assertEqual(response_data['floorplans'][floorplan6]['unitCount'], 14)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_two']['total_rent'], 3247)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_two']['average_rent'], 1623.5)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_90]['count'], 4)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_90]['total_rent'], 6404)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_90]['average_rent'], 1601.0)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_60]['count'], 3)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_60]['total_rent'], 4954)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_60]['average_rent'], 1651.33)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_30]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_30]['total_rent'], 1550)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_30]['average_rent'], 1550.0)
    
        floorplan7 = os.environ.get('03_TEST_FILE_FLOORPLAN_7')
        self.assertEqual(response_data['floorplans'][floorplan7]['avgRent'], 1511.2)
        self.assertEqual(response_data['floorplans'][floorplan7]['sumRent'], 15112)
        self.assertEqual(response_data['floorplans'][floorplan7]['avgMarket'], 1740.0)
        self.assertEqual(response_data['floorplans'][floorplan7]['sumMarket'], 19140)
        self.assertEqual(response_data['floorplans'][floorplan7]['unitCount'], 11)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_two']['total_rent'], 3090)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_two']['average_rent'], 1545.0)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_90]['count'], 4)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_90]['total_rent'], 5990)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_90]['average_rent'], 1497.5)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_60]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_60]['total_rent'], 1550)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_60]['average_rent'], 1550.0)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_30]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_30]['total_rent'], 1550)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_30]['average_rent'], 1550.0)

        floorplan8 = os.environ.get('03_TEST_FILE_FLOORPLAN_8')
        self.assertEqual(response_data['floorplans'][floorplan8]['avgRent'], 1739.0)
        self.assertEqual(response_data['floorplans'][floorplan8]['sumRent'], 1739)
        self.assertEqual(response_data['floorplans'][floorplan8]['avgMarket'], 1950.0)
        self.assertEqual(response_data['floorplans'][floorplan8]['sumMarket'], 1950)
        self.assertEqual(response_data['floorplans'][floorplan8]['unitCount'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_two']['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_two']['total_rent'], 1739)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_two']['average_rent'], 1739.0)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_leases'][days_90]['average_rent'], 0.0)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_leases'][days_60]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_leases'][days_30]['average_rent'], 0)

        floorplan9 = os.environ.get('03_TEST_FILE_FLOORPLAN_9')
        self.assertEqual(response_data['floorplans'][floorplan9]['avgRent'], 1740.0)
        self.assertEqual(response_data['floorplans'][floorplan9]['sumRent'], 8700)
        self.assertEqual(response_data['floorplans'][floorplan9]['avgMarket'], 1955.0)
        self.assertEqual(response_data['floorplans'][floorplan9]['sumMarket'], 9775)
        self.assertEqual(response_data['floorplans'][floorplan9]['unitCount'], 5)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_two']['total_rent'], 3167)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_two']['average_rent'], 1583.5)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_leases'][days_90]['average_rent'], 0.0)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_leases'][days_60]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_leases'][days_30]['average_rent'], 0)

        floorplan10 = os.environ.get('03_TEST_FILE_FLOORPLAN_10')
        self.assertEqual(response_data['floorplans'][floorplan10]['avgRent'], 1766.0)
        self.assertEqual(response_data['floorplans'][floorplan10]['sumRent'], 8830)
        self.assertEqual(response_data['floorplans'][floorplan10]['avgMarket'], 1950.0)
        self.assertEqual(response_data['floorplans'][floorplan10]['sumMarket'], 13650)
        self.assertEqual(response_data['floorplans'][floorplan10]['unitCount'], 7)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_two']['total_rent'], 3639)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_two']['average_rent'], 1819.5)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_90]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_90]['total_rent'], 1800)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_90]['average_rent'], 1800.0)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_60]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_60]['total_rent'], 1800)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_60]['average_rent'], 1800)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_30]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_30]['total_rent'], 1800)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_30]['average_rent'], 1800)




















    
    # Tear down function to clean data from the test MongoDB
    def tearDown(self):
        # Delete all documents in the dat collection
        try:
            data_collection.delete_many({})
        except Exception as e:
            print(f"An error occurred during teardown: {e}")