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
        file_name = os.environ.get('01_TEST_FILE_NAME')
        objectId = self.upload_test_file(file_name)
        response = self.client.get(self.read_data_url, {'objectId': objectId}, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response_data = json.loads(response.content)[0]

        self.assertEqual(response_data['asOf'], os.environ.get('01_TEST_FILE_AS_OF'))
        self.assertEqual(response_data['location']['building'], os.environ.get('01_TEST_FILE_LOCATION'))
        self.assertEqual(response_data['totalUnits'], 15)
        self.assertEqual(response_data['totalBalance'], -2419.23)

        self.assertEqual(response_data['vacancy']['Occupied']['count'], 6)
        self.assertEqual(response_data['vacancy']['Vacant']['count'], 9)
        self.assertEqual(response_data['vacancy']['upcoming']['count'], 4)
       
        self.assertEqual(response_data['lossToLease']['marketSum'], 20370)
        self.assertEqual(response_data['lossToLease']['rentIncome'], 6276)

        # Floor plan analysis testing
        days_90 = 'last_90_days'
        days_60 = 'last_60_days'
        days_30 = 'last_30_days'

        floorplan01 = os.environ.get('01_TEST_FILE_FLOORPLAN_01')
        self.assertEqual(response_data['floorplans'][floorplan01]['avgRent'], 330.5)
        self.assertEqual(response_data['floorplans'][floorplan01]['sumRent'], 661)
        self.assertEqual(response_data['floorplans'][floorplan01]['avgMarket'], 750.0)
        self.assertEqual(response_data['floorplans'][floorplan01]['sumMarket'], 2250)
        self.assertEqual(response_data['floorplans'][floorplan01]['unitCount'], 3)
        self.assertEqual(response_data['floorplans'][floorplan01]['avgSqft'], 600.0)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_two']['total_rent'], 661)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_two']['average_rent'], 330.5)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_90]['average_rent'], 0.0)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_60]['average_rent'], 0.0)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_30]['average_rent'], 0)

        floorplan02 = os.environ.get('01_TEST_FILE_FLOORPLAN_02')
        self.assertEqual(response_data['floorplans'][floorplan02]['avgRent'], 830.0)
        self.assertEqual(response_data['floorplans'][floorplan02]['sumRent'], 830)
        self.assertEqual(response_data['floorplans'][floorplan02]['avgMarket'], 875.0)
        self.assertEqual(response_data['floorplans'][floorplan02]['sumMarket'], 875)
        self.assertEqual(response_data['floorplans'][floorplan02]['unitCount'], 1)
        self.assertEqual(response_data['floorplans'][floorplan02]['avgSqft'], 850.0)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_two']['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_two']['total_rent'], 830)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_two']['average_rent'], 830.0)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_leases'][days_90]['average_rent'], 0.0)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_leases'][days_60]['average_rent'], 0.0)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_leases'][days_30]['average_rent'], 0)

        floorplan03 = os.environ.get('01_TEST_FILE_FLOORPLAN_03')
        self.assertEqual(response_data['floorplans'][floorplan03]['avgRent'], 1595.0)
        self.assertEqual(response_data['floorplans'][floorplan03]['sumRent'], 3190)
        self.assertEqual(response_data['floorplans'][floorplan03]['avgMarket'], 1495.0)
        self.assertEqual(response_data['floorplans'][floorplan03]['sumMarket'], 4485)
        self.assertEqual(response_data['floorplans'][floorplan03]['unitCount'], 3)
        self.assertEqual(response_data['floorplans'][floorplan03]['avgSqft'], 750.0)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_two']['total_rent'], 3190)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_two']['average_rent'], 1595.0)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_leases'][days_90]['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_leases'][days_90]['total_rent'], 3190)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_leases'][days_90]['average_rent'], 1595.0)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_leases'][days_60]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_leases'][days_60]['total_rent'], 1595)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_leases'][days_60]['average_rent'], 1595.0)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_leases'][days_30]['average_rent'], 0)
        
        floorplan04 = os.environ.get('01_TEST_FILE_FLOORPLAN_04')
        self.assertEqual(response_data['floorplans'][floorplan04]['avgRent'], 1595.0)
        self.assertEqual(response_data['floorplans'][floorplan04]['sumRent'], 1595)
        self.assertEqual(response_data['floorplans'][floorplan04]['avgMarket'], 1595.0)
        self.assertEqual(response_data['floorplans'][floorplan04]['sumMarket'], 1595)
        self.assertEqual(response_data['floorplans'][floorplan04]['unitCount'], 1)
        self.assertEqual(response_data['floorplans'][floorplan04]['avgSqft'], 750.0)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_two']['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_two']['total_rent'], 1595)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_two']['average_rent'], 1595.0)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_leases'][days_90]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_leases'][days_90]['total_rent'], 1595)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_leases'][days_90]['average_rent'], 1595.0)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_leases'][days_60]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_leases'][days_60]['total_rent'], 1595)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_leases'][days_60]['average_rent'], 1595.0)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_leases'][days_30]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_leases'][days_30]['total_rent'], 1595)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_leases'][days_30]['average_rent'], 1595.0)

        floorplan05 = os.environ.get('01_TEST_FILE_FLOORPLAN_05')
        self.assertEqual(response_data['floorplans'][floorplan05]['avgRent'], 0)
        self.assertEqual(response_data['floorplans'][floorplan05]['sumRent'], 0)
        self.assertEqual(response_data['floorplans'][floorplan05]['avgMarket'], 1620.0)
        self.assertEqual(response_data['floorplans'][floorplan05]['sumMarket'], 3240)
        self.assertEqual(response_data['floorplans'][floorplan05]['unitCount'], 2)
        self.assertEqual(response_data['floorplans'][floorplan05]['avgSqft'], 750.0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_two']['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_two']['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_two']['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_leases'][days_90]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_leases'][days_60]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_leases'][days_30]['average_rent'], 0)
        
        floorplan06 = os.environ.get('01_TEST_FILE_FLOORPLAN_06')
        self.assertEqual(response_data['floorplans'][floorplan06]['avgRent'], 0)
        self.assertEqual(response_data['floorplans'][floorplan06]['sumRent'], 0)
        self.assertEqual(response_data['floorplans'][floorplan06]['avgMarket'], 1545.0)
        self.assertEqual(response_data['floorplans'][floorplan06]['sumMarket'], 1545)
        self.assertEqual(response_data['floorplans'][floorplan06]['unitCount'], 1)
        self.assertEqual(response_data['floorplans'][floorplan06]['avgSqft'], 750.0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_two']['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_two']['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_two']['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_leases'][days_90]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_leases'][days_60]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_leases'][days_30]['average_rent'], 0)

        floorplan07 = os.environ.get('01_TEST_FILE_FLOORPLAN_07')
        self.assertEqual(response_data['floorplans'][floorplan07]['avgRent'], 0)
        self.assertEqual(response_data['floorplans'][floorplan07]['sumRent'], 0)
        self.assertEqual(response_data['floorplans'][floorplan07]['avgMarket'], 1645.0)
        self.assertEqual(response_data['floorplans'][floorplan07]['sumMarket'], 3290)
        self.assertEqual(response_data['floorplans'][floorplan07]['unitCount'], 2)
        self.assertEqual(response_data['floorplans'][floorplan07]['avgSqft'], 750.0)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_two']['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_two']['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_two']['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_leases'][days_90]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_leases'][days_60]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_leases'][days_30]['average_rent'], 0)

        floorplan08 = os.environ.get('01_TEST_FILE_FLOORPLAN_08')
        self.assertEqual(response_data['floorplans'][floorplan08]['avgRent'], 0)
        self.assertEqual(response_data['floorplans'][floorplan08]['sumRent'], 0)
        self.assertEqual(response_data['floorplans'][floorplan08]['avgMarket'], 1545.0)
        self.assertEqual(response_data['floorplans'][floorplan08]['sumMarket'], 1545)
        self.assertEqual(response_data['floorplans'][floorplan08]['unitCount'], 1)
        self.assertEqual(response_data['floorplans'][floorplan08]['avgSqft'], 850.0)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_two']['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_two']['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_two']['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_leases'][days_90]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_leases'][days_60]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_leases'][days_30]['average_rent'], 0)

        floorplan09 = os.environ.get('01_TEST_FILE_FLOORPLAN_09')
        self.assertEqual(response_data['floorplans'][floorplan09]['avgRent'], 0)
        self.assertEqual(response_data['floorplans'][floorplan09]['sumRent'], 0)
        self.assertEqual(response_data['floorplans'][floorplan09]['avgMarket'], 1545.0)
        self.assertEqual(response_data['floorplans'][floorplan09]['sumMarket'], 1545)
        self.assertEqual(response_data['floorplans'][floorplan09]['unitCount'], 1)
        self.assertEqual(response_data['floorplans'][floorplan09]['avgSqft'], 850.0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_two']['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_two']['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_two']['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_leases'][days_90]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_leases'][days_60]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_leases'][days_30]['average_rent'], 0)


    # Tear down function to clean data from the test MongoDB
    def tearDown(self):
        # Delete all documents in the dat collection
        try:
            data_collection.delete_many({})
        except Exception as e:
            print(f"An error occurred during teardown: {e}")