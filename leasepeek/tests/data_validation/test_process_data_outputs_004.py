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
        file_name = os.environ.get('04_TEST_FILE_NAME')
        objectId = self.upload_test_file(file_name)
        response = self.client.get(self.read_data_url, {'objectId': objectId}, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response_data = json.loads(response.content)[0]


        self.assertEqual(response_data['asOf'], os.environ.get('04_TEST_FILE_AS_OF'))
        self.assertEqual(response_data['location'], os.environ.get('04_TEST_FILE_LOCATION'))
        self.assertEqual(response_data['totalUnits'], 324)
        self.assertEqual(response_data['totalBalance'], -4817.10)
        
        self.assertEqual(response_data['vacancy']['Occupied'], 260)
        self.assertEqual(response_data['vacancy']['Vacant'], 64)
        self.assertEqual(response_data['vacancy']['Applicant'], 16)
        self.assertEqual(response_data['vacancy']['Pending renewal'], 3)
       
        self.assertEqual(response_data['lossToLease']['marketSum'], 560385)
        self.assertEqual(response_data['lossToLease']['rentIncome'], 401055)

        # Floor plan analysis testing
        days_90 = 'last_90_days'
        days_60 = 'last_60_days'
        days_30 = 'last_30_days'

        floorplan01 = os.environ.get('04_TEST_FILE_FLOORPLAN_01')
        self.assertEqual(response_data['floorplans'][floorplan01]['avgRent'], 1364.5)
        self.assertEqual(response_data['floorplans'][floorplan01]['sumRent'], 27290)
        self.assertEqual(response_data['floorplans'][floorplan01]['avgMarket'], 1500.0)
        self.assertEqual(response_data['floorplans'][floorplan01]['sumMarket'], 31500)
        self.assertEqual(response_data['floorplans'][floorplan01]['unitCount'], 21)
        self.assertEqual(response_data['floorplans'][floorplan01]['avgSqft'], 657.0)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_two']['total_rent'], 2800)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_two']['average_rent'], 1400.0)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_90]['count'], 4)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_90]['total_rent'], 5500)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_90]['average_rent'], 1375.0)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_60]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_60]['total_rent'], 1450)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_60]['average_rent'], 1450.0)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan01]['recent_leases'][days_30]['average_rent'], 0)

        floorplan02 = os.environ.get('04_TEST_FILE_FLOORPLAN_02')
        self.assertEqual(response_data['floorplans'][floorplan02]['unitCount'], 16)
        self.assertEqual(response_data['floorplans'][floorplan02]['avgSqft'], 705.0)
        self.assertEqual(response_data['floorplans'][floorplan02]['avgRent'], 1434.69)
        self.assertEqual(response_data['floorplans'][floorplan02]['sumRent'], 22955)
        self.assertEqual(response_data['floorplans'][floorplan02]['avgMarket'], 1600.0)
        self.assertEqual(response_data['floorplans'][floorplan02]['sumMarket'], 25600)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_two']['total_rent'], 2800)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_two']['average_rent'], 1400.0)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_leases'][days_90]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_leases'][days_60]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan02]['recent_leases'][days_30]['average_rent'], 0)

        floorplan03 = os.environ.get('04_TEST_FILE_FLOORPLAN_03')
        self.assertEqual(response_data['floorplans'][floorplan03]['unitCount'], 31)
        self.assertEqual(response_data['floorplans'][floorplan03]['avgSqft'], 704.0)
        self.assertEqual(response_data['floorplans'][floorplan03]['avgRent'], 1423.06)
        self.assertEqual(response_data['floorplans'][floorplan03]['sumRent'], 44115)
        self.assertEqual(response_data['floorplans'][floorplan03]['avgMarket'], 1530.0)
        self.assertEqual(response_data['floorplans'][floorplan03]['sumMarket'], 47430)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_two']['total_rent'], 2850)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_two']['average_rent'], 1425.0)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_leases'][days_90]['count'], 14)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_leases'][days_90]['total_rent'], 19905)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_leases'][days_90]['average_rent'], 1421.79)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_leases'][days_60]['count'], 8)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_leases'][days_60]['total_rent'], 11535)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_leases'][days_60]['average_rent'], 1441.88)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_leases'][days_30]['count'], 7)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_leases'][days_30]['total_rent'], 10140)
        self.assertEqual(response_data['recentLeases'][floorplan03]['recent_leases'][days_30]['average_rent'], 1448.57)

        floorplan04 = os.environ.get('04_TEST_FILE_FLOORPLAN_04')
        self.assertEqual(response_data['floorplans'][floorplan04]['unitCount'], 27)
        self.assertEqual(response_data['floorplans'][floorplan04]['avgSqft'], 706.0)
        self.assertEqual(response_data['floorplans'][floorplan04]['avgRent'], 1418.15)
        self.assertEqual(response_data['floorplans'][floorplan04]['sumRent'], 38290)
        self.assertEqual(response_data['floorplans'][floorplan04]['avgMarket'], 1540.0)
        self.assertEqual(response_data['floorplans'][floorplan04]['sumMarket'], 41580)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_two']['total_rent'], 2980)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_two']['average_rent'], 1490.0)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_leases'][days_90]['count'], 9)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_leases'][days_90]['total_rent'], 11920)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_leases'][days_90]['average_rent'], 1324.44)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_leases'][days_60]['count'], 5)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_leases'][days_60]['total_rent'], 5960)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_leases'][days_60]['average_rent'], 1192.0)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_leases'][days_30]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_leases'][days_30]['total_rent'], 1490)
        self.assertEqual(response_data['recentLeases'][floorplan04]['recent_leases'][days_30]['average_rent'], 1490.0)

        floorplan05 = os.environ.get('04_TEST_FILE_FLOORPLAN_05')
        self.assertEqual(response_data['floorplans'][floorplan05]['unitCount'], 4)
        self.assertEqual(response_data['floorplans'][floorplan05]['avgSqft'], 758.0)
        self.assertEqual(response_data['floorplans'][floorplan05]['avgRent'], 1555.0)
        self.assertEqual(response_data['floorplans'][floorplan05]['sumRent'], 6220)
        self.assertEqual(response_data['floorplans'][floorplan05]['avgMarket'], 1715.0)
        self.assertEqual(response_data['floorplans'][floorplan05]['sumMarket'], 6860)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_two']['total_rent'], 3080)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_two']['average_rent'], 1540.0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_leases'][days_90]['average_rent'], 0.0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_leases'][days_60]['average_rent'], 0.0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan05]['recent_leases'][days_30]['average_rent'], 0.0)

        floorplan06 = os.environ.get('04_TEST_FILE_FLOORPLAN_06')
        self.assertEqual(response_data['floorplans'][floorplan06]['unitCount'], 8)
        self.assertEqual(response_data['floorplans'][floorplan06]['avgSqft'], 798.0)
        self.assertEqual(response_data['floorplans'][floorplan06]['avgRent'], 0.0)
        self.assertEqual(response_data['floorplans'][floorplan06]['sumRent'], 0)
        self.assertEqual(response_data['floorplans'][floorplan06]['avgMarket'], 1745.0)
        self.assertEqual(response_data['floorplans'][floorplan06]['sumMarket'], 13960)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_two']['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_two']['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_two']['average_rent'], 0.0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_leases'][days_90]['average_rent'], 0.0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_leases'][days_60]['average_rent'], 0.0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan06]['recent_leases'][days_30]['average_rent'], 0.0)

        floorplan07 = os.environ.get('04_TEST_FILE_FLOORPLAN_07')
        self.assertEqual(response_data['floorplans'][floorplan07]['unitCount'], 99)
        self.assertEqual(response_data['floorplans'][floorplan07]['avgSqft'], 944.0)
        self.assertEqual(response_data['floorplans'][floorplan07]['avgRent'], 1721.76)
        self.assertEqual(response_data['floorplans'][floorplan07]['sumRent'], 117080)
        self.assertEqual(response_data['floorplans'][floorplan07]['avgMarket'], 1855.0)
        self.assertEqual(response_data['floorplans'][floorplan07]['sumMarket'], 183645)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_two']['total_rent'], 3350)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_two']['average_rent'], 1675.0)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_leases'][days_90]['count'], 37)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_leases'][days_90]['total_rent'], 62490)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_leases'][days_90]['average_rent'], 1688.92)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_leases'][days_60]['count'], 24)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_leases'][days_60]['total_rent'], 40390)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_leases'][days_60]['average_rent'], 1682.92)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_leases'][days_30]['count'], 9)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_leases'][days_30]['total_rent'], 15050)
        self.assertEqual(response_data['recentLeases'][floorplan07]['recent_leases'][days_30]['average_rent'], 1672.22)

        floorplan08 = os.environ.get('04_TEST_FILE_FLOORPLAN_08')
        self.assertEqual(response_data['floorplans'][floorplan08]['unitCount'], 12)
        self.assertEqual(response_data['floorplans'][floorplan08]['avgSqft'], 1168.0)
        self.assertEqual(response_data['floorplans'][floorplan08]['avgRent'], 2140.0)
        self.assertEqual(response_data['floorplans'][floorplan08]['sumRent'], 25680)
        self.assertEqual(response_data['floorplans'][floorplan08]['avgMarket'], 2270.0)
        self.assertEqual(response_data['floorplans'][floorplan08]['sumMarket'], 27240)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_two']['total_rent'], 4280)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_two']['average_rent'], 2140.0)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_leases'][days_90]['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_leases'][days_90]['total_rent'], 4280)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_leases'][days_90]['average_rent'], 2140.0)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_leases'][days_60]['average_rent'], 0.0)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan08]['recent_leases'][days_30]['average_rent'], 0.0)

        floorplan09 = os.environ.get('04_TEST_FILE_FLOORPLAN_09')
        self.assertEqual(response_data['floorplans'][floorplan09]['unitCount'], 6)
        self.assertEqual(response_data['floorplans'][floorplan09]['avgSqft'], 1133.0)
        self.assertEqual(response_data['floorplans'][floorplan09]['avgRent'], 0.0)
        self.assertEqual(response_data['floorplans'][floorplan09]['sumRent'], 0)
        self.assertEqual(response_data['floorplans'][floorplan09]['avgMarket'], 2275.0)
        self.assertEqual(response_data['floorplans'][floorplan09]['sumMarket'], 13650)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_two']['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_two']['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_two']['average_rent'], 0.0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_leases'][days_90]['average_rent'], 0.0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_leases'][days_60]['average_rent'], 0.0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan09]['recent_leases'][days_30]['average_rent'], 0.0)

        floorplan10 = os.environ.get('04_TEST_FILE_FLOORPLAN_10')
        self.assertEqual(response_data['floorplans'][floorplan10]['unitCount'], 24)
        self.assertEqual(response_data['floorplans'][floorplan10]['avgSqft'], 1157.0)
        self.assertEqual(response_data['floorplans'][floorplan10]['avgRent'], 2275.0)
        self.assertEqual(response_data['floorplans'][floorplan10]['sumRent'], 20475)
        self.assertEqual(response_data['floorplans'][floorplan10]['avgMarket'], 2325.0)
        self.assertEqual(response_data['floorplans'][floorplan10]['sumMarket'], 55800)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_two']['total_rent'], 4550)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_two']['average_rent'], 2275.0)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_90]['count'], 5)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_90]['total_rent'], 11375)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_90]['average_rent'], 2275.0)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_60]['count'], 4)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_60]['total_rent'], 9100)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_60]['average_rent'], 2275.0)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_30]['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_30]['total_rent'], 4550)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_30]['average_rent'], 2275.0)

        floorplan11 = os.environ.get('04_TEST_FILE_FLOORPLAN_11')
        self.assertEqual(response_data['floorplans'][floorplan11]['unitCount'], 16)
        self.assertEqual(response_data['floorplans'][floorplan11]['avgSqft'], 1318.0)
        self.assertEqual(response_data['floorplans'][floorplan11]['avgRent'], 2520.0)
        self.assertEqual(response_data['floorplans'][floorplan11]['sumRent'], 35280)
        self.assertEqual(response_data['floorplans'][floorplan11]['avgMarket'], 2570.0)
        self.assertEqual(response_data['floorplans'][floorplan11]['sumMarket'], 41120)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_two']['total_rent'], 5040)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_two']['average_rent'], 2520.0)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_leases'][days_90]['count'], 7)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_leases'][days_90]['total_rent'], 17640)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_leases'][days_90]['average_rent'], 2520.0)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_leases'][days_60]['count'], 6)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_leases'][days_60]['total_rent'], 15120)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_leases'][days_60]['average_rent'], 2520.0)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_leases'][days_30]['count'], 3)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_leases'][days_30]['total_rent'], 7560)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_leases'][days_30]['average_rent'], 2520.0)

        floorplan12 = os.environ.get('04_TEST_FILE_FLOORPLAN_12')
        self.assertEqual(response_data['floorplans'][floorplan12]['unitCount'], 57)
        self.assertEqual(response_data['floorplans'][floorplan12]['avgSqft'], 534.0)
        self.assertEqual(response_data['floorplans'][floorplan12]['avgRent'], 1078.57)
        self.assertEqual(response_data['floorplans'][floorplan12]['sumRent'], 60400)
        self.assertEqual(response_data['floorplans'][floorplan12]['avgMarket'], 1200.0)
        self.assertEqual(response_data['floorplans'][floorplan12]['sumMarket'], 68400)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_two']['total_rent'], 2240)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_two']['average_rent'], 1120.0)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_leases'][days_90]['count'], 5)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_leases'][days_90]['total_rent'], 5510)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_leases'][days_90]['average_rent'], 1102.0)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_leases'][days_60]['count'], 3)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_leases'][days_60]['total_rent'], 3330)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_leases'][days_60]['average_rent'], 1110.0)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_leases'][days_30]['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_leases'][days_30]['total_rent'], 2240)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_leases'][days_30]['average_rent'], 1120.0)

        floorplan13 = os.environ.get('04_TEST_FILE_FLOORPLAN_13')
        self.assertEqual(response_data['floorplans'][floorplan13]['unitCount'], 3)
        self.assertEqual(response_data['floorplans'][floorplan13]['avgSqft'], 534.0)
        self.assertEqual(response_data['floorplans'][floorplan13]['avgRent'], 1090.0)
        self.assertEqual(response_data['floorplans'][floorplan13]['sumRent'], 3270)
        self.assertEqual(response_data['floorplans'][floorplan13]['avgMarket'], 1200.0)
        self.assertEqual(response_data['floorplans'][floorplan13]['sumMarket'], 3600)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_two']['total_rent'], 2180)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_two']['average_rent'], 1090.0)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_leases'][days_90]['average_rent'], 0.0)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_leases'][days_60]['average_rent'], 0.0)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_leases'][days_30]['count'], 0) 
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_leases'][days_30]['average_rent'], 0.0)
        

    # Tear down function to clean data from the test MongoDB
    def tearDown(self):
        # Delete all documents in the dat collection
        try:
            data_collection.delete_many({})
        except Exception as e:
            print(f"An error occurred during teardown: {e}")