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
        file_name = os.environ.get('06_TEST_FILE_NAME')
        objectId = self.upload_test_file(file_name)
        response = self.client.get(self.read_data_url, {'objectId': objectId}, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response_data = json.loads(response.content)[0]


        self.assertEqual(response_data['asOf'], os.environ.get('06_TEST_FILE_AS_OF'))
        self.assertEqual(response_data['location'], os.environ.get('06_TEST_FILE_LOCATION'))
        self.assertEqual(response_data['totalUnits'], 280)
        self.assertEqual(response_data['vacancy']['Occupied'], 251)
        self.assertEqual(response_data['vacancy']['Vacant'], 27)
        self.assertEqual(response_data['vacancy']['NonRev'], 2)
    
        self.assertEqual(response_data['lossToLease']['marketSum'], 291185)
        self.assertEqual(response_data['lossToLease']['rentIncome'], 257672)

        # Floor plan analysis testing
        days_90 = 'last_90_days'
        days_60 = 'last_60_days'
        days_30 = 'last_30_days'

        floorplan1 = os.environ.get('06_TEST_FILE_FLOORPLAN_1')
        self.assertEqual(response_data['floorplans'][floorplan1]['avgRent'], 990.03)
        self.assertEqual(response_data['floorplans'][floorplan1]['sumRent'], 61382)
        self.assertEqual(response_data['floorplans'][floorplan1]['avgMarket'], 1016.98)
        self.assertEqual(response_data['floorplans'][floorplan1]['sumMarket'], 64070)
        self.assertEqual(response_data['floorplans'][floorplan1]['unitCount'], 63)
        self.assertEqual(response_data['floorplans'][floorplan1]['avgSqft'], 540.0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_two']['total_rent'], 2294)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_two']['average_rent'], 1147.0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_90]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_60]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_30]['average_rent'], 0)

        floorplan2 = os.environ.get('06_TEST_FILE_FLOORPLAN_2')
        self.assertEqual(response_data['floorplans'][floorplan2]['avgRent'], 1201.31)
        self.assertEqual(response_data['floorplans'][floorplan2]['sumRent'], 85293)
        self.assertEqual(response_data['floorplans'][floorplan2]['avgMarket'], 1156.48)
        self.assertEqual(response_data['floorplans'][floorplan2]['sumMarket'], 93675)
        self.assertEqual(response_data['floorplans'][floorplan2]['unitCount'], 81)
        self.assertEqual(response_data['floorplans'][floorplan2]['avgSqft'], 540.0)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_two']['total_rent'], 2365)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_two']['average_rent'], 1182.5)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_90]['count'], 16)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_90]['total_rent'], 19190)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_90]['average_rent'], 1199.38)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_60]['count'], 10)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_60]['total_rent'], 12035)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_60]['average_rent'], 1203.5)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_30]['count'], 6)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_30]['total_rent'], 7185)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_30]['average_rent'], 1197.5)

        floorplan3 = os.environ.get('06_TEST_FILE_FLOORPLAN_3')
        self.assertEqual(response_data['floorplans'][floorplan3]['avgRent'], 972.83)
        self.assertEqual(response_data['floorplans'][floorplan3]['sumRent'], 63234)
        self.assertEqual(response_data['floorplans'][floorplan3]['avgMarket'], 1019.75)
        self.assertEqual(response_data['floorplans'][floorplan3]['sumMarket'], 81580)
        self.assertEqual(response_data['floorplans'][floorplan3]['unitCount'], 80)
        self.assertEqual(response_data['floorplans'][floorplan3]['avgSqft'], 380.0)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_two']['total_rent'], 1865)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_two']['average_rent'], 932.5)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_90]['count'], 15)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_90]['total_rent'], 14520)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_90]['average_rent'], 968.0)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_60]['count'], 10)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_60]['total_rent'], 9515)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_60]['average_rent'], 951.5)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_30]['count'], 5)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_30]['total_rent'], 4735)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_30]['average_rent'], 947.0)

        floorplan4 = os.environ.get('06_TEST_FILE_FLOORPLAN_4')
        self.assertEqual(response_data['floorplans'][floorplan4]['avgRent'], 830.84)
        self.assertEqual(response_data['floorplans'][floorplan4]['sumRent'], 37388)
        self.assertEqual(response_data['floorplans'][floorplan4]['avgMarket'], 878.23)
        self.assertEqual(response_data['floorplans'][floorplan4]['sumMarket'], 42155)
        self.assertEqual(response_data['floorplans'][floorplan4]['unitCount'], 48)
        self.assertEqual(response_data['floorplans'][floorplan4]['avgSqft'], 380.0)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_two']['total_rent'], 1637)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_two']['average_rent'], 818.5)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_90]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_60]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_30]['average_rent'], 0)

        floorplan5 = os.environ.get('06_TEST_FILE_FLOORPLAN_5')
        self.assertEqual(response_data['floorplans'][floorplan5]['avgRent'], 1272.0)
        self.assertEqual(response_data['floorplans'][floorplan5]['sumRent'], 2544)
        self.assertEqual(response_data['floorplans'][floorplan5]['avgMarket'], 1205.0)
        self.assertEqual(response_data['floorplans'][floorplan5]['sumMarket'], 2410)
        self.assertEqual(response_data['floorplans'][floorplan5]['unitCount'], 2)
        self.assertEqual(response_data['floorplans'][floorplan5]['avgSqft'], 866.0)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_two']['total_rent'], 2544)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_two']['average_rent'], 1272.0)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_90]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_60]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_30]['average_rent'], 0)

        floorplan6 = os.environ.get('06_TEST_FILE_FLOORPLAN_6')
        self.assertEqual(response_data['floorplans'][floorplan6]['avgRent'], 1485.0)
        self.assertEqual(response_data['floorplans'][floorplan6]['sumRent'], 2970)
        self.assertEqual(response_data['floorplans'][floorplan6]['avgMarket'], 1367.5)
        self.assertEqual(response_data['floorplans'][floorplan6]['sumMarket'], 2735)
        self.assertEqual(response_data['floorplans'][floorplan6]['unitCount'], 2)
        self.assertEqual(response_data['floorplans'][floorplan6]['avgSqft'], 866.0)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_two']['total_rent'], 2970)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_two']['average_rent'], 1485.0)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_90]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_90]['total_rent'], 1445)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_90]['average_rent'], 1445.0)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_60]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_60]['total_rent'], 1445)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_60]['average_rent'], 1445.0)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_30]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_30]['total_rent'], 1445)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_30]['average_rent'], 1445.0)

        floorplan7 = os.environ.get('06_TEST_FILE_FLOORPLAN_7')
        self.assertEqual(response_data['floorplans'][floorplan7]['avgRent'], 1215.25)
        self.assertEqual(response_data['floorplans'][floorplan7]['sumRent'], 4861)
        self.assertEqual(response_data['floorplans'][floorplan7]['avgMarket'], 1140.0)
        self.assertEqual(response_data['floorplans'][floorplan7]['sumMarket'], 4560)
        self.assertEqual(response_data['floorplans'][floorplan7]['unitCount'], 4)
        self.assertEqual(response_data['floorplans'][floorplan7]['avgSqft'], 825.0)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_two']['total_rent'], 2299)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_two']['average_rent'], 1149.5)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_90]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_60]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_30]['average_rent'], 0)


    # Tear down function to clean data from the test MongoDB
    def tearDown(self):
        # Delete all documents in the dat collection
        try:
            data_collection.delete_many({})
        except Exception as e:
            print(f"An error occurred during teardown: {e}")