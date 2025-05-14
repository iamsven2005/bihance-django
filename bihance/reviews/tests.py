# Integration testing (models, serializers, utils, views)
# Negative test cases? 

from django.test import TestCase
from rest_framework.test import APIClient
from tests.objects import get_employee, get_employer, get_job, get_application
from utils.utils import terminate_current_connections


terminate_current_connections()

class ReviewsAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Performed once before all tests
        # Create test objects
        cls.employee = get_employee()
        cls.employer = get_employer()
        cls.job = get_job()
        cls.application = get_application()

        # Base url for all reviews endpoint
        cls.base_url = '/api/reviews/'
        
    def auth_employee(self): 
        self.client = APIClient() 
        self.client.force_authenticate(user=self.employee)

    def auth_employer(self): 
        self.client = APIClient() 
        self.client.force_authenticate(user=self.employer)

    # PATCH
    def test_update_review(self): 
        application_id = self.application.application_id

        self.auth_employee()
        data = { 
            "content": "This job application process was so ass.",
            "rating": "1"
        }
        response = self.client.patch(f"{self.base_url}{application_id}/", data, format="json")
        self.assertEqual(response.status_code, 200)


        self.auth_employer()
        data = {
            "content": "This applicant was soo fucking rude."
        }
        response = self.client.patch(f"{self.base_url}{application_id}/", data, format="json")
        self.assertEqual(response.status_code, 200)


