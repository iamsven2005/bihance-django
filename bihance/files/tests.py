# Integration testing (models, serializers, utils, views)
# Negative test cases? 

from .models import Files
from django.test import TestCase
from rest_framework.test import APIClient
from tests.objects import get_employee, get_employer, get_job, get_application, get_message
from tests.utils import verify_file_shape
from utils.utils import terminate_current_connections


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
        cls.message = get_message()

        # Base url for all applications endpoint
        cls.base_url = '/api/files/'

        
    def setUp(self): 
        self.client = APIClient() 
        self.client.force_authenticate(user=self.employee)


    def test_all(self): 
        self.create_file()
        self.get_files()
        self.delete_files()

    # POST
    def create_file(self): 
        data = { 
            "fileKey": "YX7xA2cz6RDlzAiEhYyaEZD8247KIlgAHiNfeSLWX1y5Ju63",
            "fileUrl": "https://bhg1of7blh.ufs.sh/f/YX7xA2cz6RDlzAiEhYyaEZD8247KIlgAHiNfeSLWX1y5Ju63",
            "fileName": "catto",
            "fileType": "image/jpeg",
            "fileSize": 64755,
            "associatedType": "Message",
            "associatedObjectId": self.message.message_id
        }

        response = self.client.post(self.base_url, data, format="json")
        self.assertEqual(response.status_code, 200)


    # GET
    def get_files(self): 
        data = {
            "associatedType": "Message",
            "associatedObjectId": self.message.message_id
        }

        response = self.client.get(self.base_url, data, format="json")
        self.assertEqual(response.status_code, 200)

        files = response.json()
        for file in files: 
            print(file)
            verify_file_shape(file)


    # DELETE
    def delete_files(self): 
        file = Files.objects.first()
        file_key = file.file_key

        response = self.client.delete(f"{self.base_url}{file_key}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Files.objects.count(), 0)


