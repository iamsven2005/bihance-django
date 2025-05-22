# Integration testing (models, serializers, utils, views)
# Negative test cases? 

from django.test import TestCase
from rest_framework.test import APIClient
from utils.utils import terminate_current_connections
from utils.tests.objects import get_employee, get_employer, get_job, get_application, get_message
from utils.tests.utils import verify_file_shape


from datetime import datetime
from django.utils.timezone import make_aware

terminate_current_connections()

class ApplicationsAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Performed once before all tests
        # Create test objects
        cls.employee = get_employee()
        cls.employer = get_employer()
        cls.job = get_job()
        cls.application = get_application()

        # Base url for all applications endpoint
        cls.base_url = '/api/jobs/'

        
    def auth_employee(self): 
        self.client = APIClient() 
        self.client.force_authenticate(user=self.employee)

    def auth_employer(self): 
        self.client = APIClient() 
        self.client.force_authenticate(user=self.employer)



    def test_get_jobs(self): 
        self.auth_employer()
      

        FIXED_DATE = make_aware(datetime(2025, 1, 1, 12, 0, 0))
        data = {
            "name": "Pundeh",
            "startDate": FIXED_DATE,
            "description": "Must be able to transform into a tree, detect glitch entities.",
            "jobRequirements": ["her", "hes", "hex"]
        }
        response = self.client.post(self.base_url, data, format="json")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(f"{self.base_url}filtered/?search=hes")
        self.assertEqual(response.status_code, 200)
        print(response.json())

    



        


    