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
        self.assertEqual(response_data['location']['building'], os.environ.get('05_TEST_FILE_LOCATION'))
        self.assertEqual(response_data['totalUnits'], 310)
        self.assertEqual(response_data['totalBalance'], -3724.23)
        
        self.assertEqual(response_data['vacancy']['Occupied']['count'], 262)
        self.assertEqual(response_data['vacancy']['Vacant']['count'], 46)
        self.assertEqual(response_data['vacancy']['Model']['count'], 2)
       
        self.assertEqual(response_data['lossToLease']['marketSum'], 542451)
        self.assertEqual(response_data['lossToLease']['rentIncome'], 461333)

        # Floor plan analysis testing
        days_90 = 'last_90_days'
        days_60 = 'last_60_days'
        days_30 = 'last_30_days'

        floorplan1 = os.environ.get('05_TEST_FILE_FLOORPLAN_1')
        self.assertEqual(response_data['floorplans'][floorplan1]['avgRent'], 1685.0)
        self.assertEqual(response_data['floorplans'][floorplan1]['sumRent'], 1685)
        self.assertEqual(response_data['floorplans'][floorplan1]['avgMarket'], 1671.67)
        self.assertEqual(response_data['floorplans'][floorplan1]['sumMarket'], 5015)
        self.assertEqual(response_data['floorplans'][floorplan1]['unitCount'], 3)
        self.assertEqual(response_data['floorplans'][floorplan1]['avgSqft'], 782.0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_two']['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_two']['total_rent'], 1685)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_two']['average_rent'], 1685.0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_90]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_60]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan1]['recent_leases'][days_30]['average_rent'], 0)

        floorplan2 = os.environ.get('05_TEST_FILE_FLOORPLAN_2')
        self.assertEqual(response_data['floorplans'][floorplan2]['avgRent'], 1642.33)
        self.assertEqual(response_data['floorplans'][floorplan2]['sumRent'], 172445)
        self.assertEqual(response_data['floorplans'][floorplan2]['avgMarket'], 1585.96)
        self.assertEqual(response_data['floorplans'][floorplan2]['sumMarket'], 182385)
        self.assertEqual(response_data['floorplans'][floorplan2]['unitCount'], 115)
        self.assertEqual(response_data['floorplans'][floorplan2]['avgSqft'], 782.0)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_two']['total_rent'], 3345)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_two']['average_rent'], 1672.5)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_90]['count'], 34)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_90]['total_rent'], 56360)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_90]['average_rent'], 1657.65)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_60]['count'], 15)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_60]['total_rent'], 25020)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_60]['average_rent'], 1668.0)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_30]['count'], 7)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_30]['total_rent'], 11690)
        self.assertEqual(response_data['recentLeases'][floorplan2]['recent_leases'][days_30]['average_rent'], 1670.0)

        floorplan3 = os.environ.get('05_TEST_FILE_FLOORPLAN_3')
        self.assertEqual(response_data['floorplans'][floorplan3]['avgRent'], 1647.86)
        self.assertEqual(response_data['floorplans'][floorplan3]['sumRent'], 11535)
        self.assertEqual(response_data['floorplans'][floorplan3]['avgMarket'], 1652.5)
        self.assertEqual(response_data['floorplans'][floorplan3]['sumMarket'], 13220)
        self.assertEqual(response_data['floorplans'][floorplan3]['unitCount'], 8)
        self.assertEqual(response_data['floorplans'][floorplan3]['avgSqft'], 782.0)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_two']['total_rent'], 3280)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_two']['average_rent'], 1640.0)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_90]['count'], 3)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_90]['total_rent'], 4945)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_90]['average_rent'], 1648.33)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_60]['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_60]['total_rent'], 3280)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_60]['average_rent'], 1640.0)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_30]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_30]['total_rent'], 1640)
        self.assertEqual(response_data['recentLeases'][floorplan3]['recent_leases'][days_30]['average_rent'], 1640.0)

        floorplan4 = os.environ.get('05_TEST_FILE_FLOORPLAN_4')
        self.assertEqual(response_data['floorplans'][floorplan4]['avgRent'], 2065.0)
        self.assertEqual(response_data['floorplans'][floorplan4]['sumRent'], 2065)
        self.assertEqual(response_data['floorplans'][floorplan4]['avgMarket'], 2065.0)
        self.assertEqual(response_data['floorplans'][floorplan4]['sumMarket'], 2065)
        self.assertEqual(response_data['floorplans'][floorplan4]['unitCount'], 1)
        self.assertEqual(response_data['floorplans'][floorplan4]['avgSqft'], 877.0)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_two']['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_two']['total_rent'], 2065)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_two']['average_rent'], 2065.0)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_90]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_60]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan4]['recent_leases'][days_30]['average_rent'], 0)

        floorplan5 = os.environ.get('05_TEST_FILE_FLOORPLAN_5')
        self.assertEqual(response_data['floorplans'][floorplan5]['avgRent'], 1537.5)
        self.assertEqual(response_data['floorplans'][floorplan5]['sumRent'], 46125)
        self.assertEqual(response_data['floorplans'][floorplan5]['avgMarket'], 1582.43)
        self.assertEqual(response_data['floorplans'][floorplan5]['sumMarket'], 55385)
        self.assertEqual(response_data['floorplans'][floorplan5]['unitCount'], 35)
        self.assertEqual(response_data['floorplans'][floorplan5]['avgSqft'], 613.0)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_two']['total_rent'], 3185)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_two']['average_rent'], 1592.5)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_90]['count'], 10)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_90]['total_rent'], 15655)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_90]['average_rent'], 1565.5)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_60]['count'], 3)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_60]['total_rent'], 4770)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_60]['average_rent'], 1590.0)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_30]['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_30]['total_rent'], 3185)
        self.assertEqual(response_data['recentLeases'][floorplan5]['recent_leases'][days_30]['average_rent'], 1592.5)

        floorplan6 = os.environ.get('05_TEST_FILE_FLOORPLAN_6')
        self.assertEqual(response_data['floorplans'][floorplan6]['avgRent'], 1760.88)
        self.assertEqual(response_data['floorplans'][floorplan6]['sumRent'], 29935)
        self.assertEqual(response_data['floorplans'][floorplan6]['avgMarket'], 1778.0)
        self.assertEqual(response_data['floorplans'][floorplan6]['sumMarket'], 35560)
        self.assertEqual(response_data['floorplans'][floorplan6]['unitCount'], 20)
        self.assertEqual(response_data['floorplans'][floorplan6]['avgSqft'], 867.0)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_two']['total_rent'], 3580)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_two']['average_rent'], 1790.0)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_90]['count'], 5)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_90]['total_rent'], 8870)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_90]['average_rent'], 1774.0)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_60]['count'], 3)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_60]['total_rent'], 5335)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_60]['average_rent'], 1778.33)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_30]['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_30]['total_rent'], 3580)
        self.assertEqual(response_data['recentLeases'][floorplan6]['recent_leases'][days_30]['average_rent'], 1790.0)

        floorplan7 = os.environ.get('05_TEST_FILE_FLOORPLAN_7')
        self.assertEqual(response_data['floorplans'][floorplan7]['avgRent'], 1933.47)
        self.assertEqual(response_data['floorplans'][floorplan7]['sumRent'], 114075)
        self.assertEqual(response_data['floorplans'][floorplan7]['avgMarket'], 1946.48)
        self.assertEqual(response_data['floorplans'][floorplan7]['sumMarket'], 124575)
        self.assertEqual(response_data['floorplans'][floorplan7]['unitCount'], 64)
        self.assertEqual(response_data['floorplans'][floorplan7]['avgSqft'], 1038.0)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_two']['total_rent'], 3900)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_two']['average_rent'], 1950.0)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_90]['count'], 17)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_90]['total_rent'], 33065)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_90]['average_rent'], 1945.0)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_60]['count'], 9)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_60]['total_rent'], 17585)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_60]['average_rent'], 1953.89)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_30]['count'], 5)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_30]['total_rent'], 9790)
        self.assertEqual(response_data['recentLeases'][floorplan7]['recent_leases'][days_30]['average_rent'], 1958.0)

        floorplan8 = os.environ.get('05_TEST_FILE_FLOORPLAN_8')
        self.assertEqual(response_data['floorplans'][floorplan8]['avgRent'], 2041.27)
        self.assertEqual(response_data['floorplans'][floorplan8]['sumRent'], 61238)
        self.assertEqual(response_data['floorplans'][floorplan8]['avgMarket'], 1947.88)
        self.assertEqual(response_data['floorplans'][floorplan8]['sumMarket'], 95446)
        self.assertEqual(response_data['floorplans'][floorplan8]['unitCount'], 49)
        self.assertEqual(response_data['floorplans'][floorplan8]['avgSqft'], 1130.0)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_two']['total_rent'], 4028)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_two']['average_rent'], 2014.0)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_leases'][days_90]['count'], 6)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_leases'][days_90]['total_rent'], 12319)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_leases'][days_90]['average_rent'], 2053.17)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_leases'][days_60]['count'], 4)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_leases'][days_60]['total_rent'], 8186)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_leases'][days_60]['average_rent'], 2046.5)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_leases'][days_30]['count'], 3)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_leases'][days_30]['total_rent'], 6107)
        self.assertEqual(response_data['recentLeases'][floorplan8]['recent_leases'][days_30]['average_rent'], 2035.67)

        floorplan9 = os.environ.get('05_TEST_FILE_FLOORPLAN_9')
        self.assertEqual(response_data['floorplans'][floorplan9]['avgRent'], 1701.67)
        self.assertEqual(response_data['floorplans'][floorplan9]['sumRent'], 5105)
        self.assertEqual(response_data['floorplans'][floorplan9]['avgMarket'], 1738.33)
        self.assertEqual(response_data['floorplans'][floorplan9]['sumMarket'], 5215)
        self.assertEqual(response_data['floorplans'][floorplan9]['unitCount'], 3)
        self.assertEqual(response_data['floorplans'][floorplan9]['avgSqft'], 825.0)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_two']['total_rent'], 3460)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_two']['average_rent'], 1730.0)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_leases'][days_90]['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_leases'][days_90]['total_rent'], 3460)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_leases'][days_90]['average_rent'], 1730.0)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_leases'][days_60]['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_leases'][days_60]['total_rent'], 3460)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_leases'][days_60]['average_rent'], 1730.0)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_leases'][days_30]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_leases'][days_30]['total_rent'], 1730)
        self.assertEqual(response_data['recentLeases'][floorplan9]['recent_leases'][days_30]['average_rent'], 1730.0)

        floorplan10 = os.environ.get('05_TEST_FILE_FLOORPLAN_10')
        self.assertEqual(response_data['floorplans'][floorplan10]['avgRent'], 1660.0)
        self.assertEqual(response_data['floorplans'][floorplan10]['sumRent'], 4980)
        self.assertEqual(response_data['floorplans'][floorplan10]['avgMarket'], 1673.33)
        self.assertEqual(response_data['floorplans'][floorplan10]['sumMarket'], 5020)
        self.assertEqual(response_data['floorplans'][floorplan10]['unitCount'], 3)
        self.assertEqual(response_data['floorplans'][floorplan10]['avgSqft'], 764.0)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_two']['total_rent'], 3315)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_two']['average_rent'], 1657.5)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_90]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_90]['total_rent'], 1665)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_90]['average_rent'], 1665.0)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_60]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_60]['total_rent'], 1665)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_60]['average_rent'], 1665.0)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_30]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_30]['total_rent'], 1665)
        self.assertEqual(response_data['recentLeases'][floorplan10]['recent_leases'][days_30]['average_rent'], 1665.0)

        floorplan11 = os.environ.get('05_TEST_FILE_FLOORPLAN_11')
        self.assertEqual(response_data['floorplans'][floorplan11]['avgRent'], 1575.0)
        self.assertEqual(response_data['floorplans'][floorplan11]['sumRent'], 1575)
        self.assertEqual(response_data['floorplans'][floorplan11]['avgMarket'], 1575.0)
        self.assertEqual(response_data['floorplans'][floorplan11]['sumMarket'], 1575)
        self.assertEqual(response_data['floorplans'][floorplan11]['unitCount'], 1)
        self.assertEqual(response_data['floorplans'][floorplan11]['avgSqft'], 697.0)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_two']['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_two']['total_rent'], 1575)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_two']['average_rent'], 1575.0)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_leases'][days_90]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_leases'][days_90]['total_rent'], 1575)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_leases'][days_90]['average_rent'], 1575.0)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_leases'][days_60]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_leases'][days_60]['total_rent'], 1575)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_leases'][days_60]['average_rent'], 1575.0)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan11]['recent_leases'][days_30]['average_rent'], 0)

        floorplan12 = os.environ.get('05_TEST_FILE_FLOORPLAN_12')
        self.assertEqual(response_data['floorplans'][floorplan12]['avgRent'], 0)
        self.assertEqual(response_data['floorplans'][floorplan12]['sumRent'], 0)
        self.assertEqual(response_data['floorplans'][floorplan12]['avgMarket'], 1950.0)
        self.assertEqual(response_data['floorplans'][floorplan12]['sumMarket'], 3900)
        self.assertEqual(response_data['floorplans'][floorplan12]['unitCount'], 2)
        self.assertEqual(response_data['floorplans'][floorplan12]['avgSqft'], 1038.0)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_two']['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_two']['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_two']['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_leases'][days_90]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_leases'][days_90]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_leases'][days_90]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_leases'][days_60]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan12]['recent_leases'][days_30]['average_rent'], 0)

        floorplan13 = os.environ.get('05_TEST_FILE_FLOORPLAN_13')
        self.assertEqual(response_data['floorplans'][floorplan13]['avgRent'], 2114.0)
        self.assertEqual(response_data['floorplans'][floorplan13]['sumRent'], 10570)
        self.assertEqual(response_data['floorplans'][floorplan13]['avgMarket'], 2181.67)
        self.assertEqual(response_data['floorplans'][floorplan13]['sumMarket'], 13090)
        self.assertEqual(response_data['floorplans'][floorplan13]['unitCount'], 6)
        self.assertEqual(response_data['floorplans'][floorplan13]['avgSqft'], 1192.0)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_two']['count'], 2)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_two']['total_rent'], 4380)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_two']['average_rent'], 2190)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_leases'][days_90]['count'], 1)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_leases'][days_90]['total_rent'], 2190)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_leases'][days_90]['average_rent'], 2190)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_leases'][days_60]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_leases'][days_60]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_leases'][days_60]['average_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_leases'][days_30]['count'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_leases'][days_30]['total_rent'], 0)
        self.assertEqual(response_data['recentLeases'][floorplan13]['recent_leases'][days_30]['average_rent'], 0)

    # Tear down function to clean data from the test MongoDB
    def tearDown(self):
        # Delete all documents in the dat collection
        try:
            data_collection.delete_many({})
        except Exception as e:
            print(f"An error occurred during teardown: {e}")