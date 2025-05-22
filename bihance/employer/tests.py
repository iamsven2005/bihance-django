# Integration testing (models, serializers, utils, views)
# Negative test cases?

from companies.models import EmployerProfile
from django.test import TestCase
from rest_framework.test import APIClient
from utils.tests.objects import get_employer
from utils.utils import terminate_current_connections

terminate_current_connections()


class EmployerAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Performed once before all tests
        # Create test objects
        cls.employer = get_employer()
        cls.base_url = "/api/employer/"

    def setUp(self):
        # Performed once before each test
        self.client = APIClient()
        self.client.force_authenticate(user=self.employer)

    def test_all(self):
        self.create_profile()
        self.edit_profile()

    # POST employer profile/company
    def create_profile(self):
        data = {
            "companyName": "BOMBADILLO CROCODILLO",
            "companyWebsite": "www.youtube.com",
        }
        response = self.client.post(self.base_url, data, format="json")
        self.assertEqual(response.status_code, 200)

        duplicated_data = {
            "companyName": "BOMBADILLO CROCODILLO",
            "companyWebsite": "www.youtube.com",
        }
        response = self.client.post(self.base_url, duplicated_data, format="json")
        self.assertEqual(response.status_code, 400)

    # PATCH employer profile/company
    def edit_profile(self):
        company_id = EmployerProfile.objects.first().company_id
        response = self.client.patch(f"{self.base_url}{company_id}/")
        self.assertEqual(response.status_code, 400)

        data = {
            "talentNeeds": ["hello", "other"],
            "otherTalentNeeds": ["pundeh", "valilkea", "other"],
        }
        response = self.client.patch(
            f"{self.base_url}{company_id}/", data, format="json"
        )
        self.assertEqual(response.status_code, 200)
