# Integration testing (models, serializers, utils, views)
# Negative test cases? 

from .models import Message, MessageFile
from django.test import TestCase
from rest_framework.test import APIClient
from tests.objects import get_employee, get_employer, get_job, get_application
from tests.utils import verify_message_shape, verify_message_file_shape
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

        # Base url for all messages endpoint
        cls.base_url = '/api/messages/'

    def auth_employee(self): 
        self.client = APIClient() 
        self.client.force_authenticate(user=self.employee)

    def auth_employer(self): 
        self.client = APIClient() 
        self.client.force_authenticate(user=self.employer)


    def test_all(self): 
        self.create_messages()
        self.get_messages()
        self.patch_message()
        self.delete_message()

    # POST
    def create_messages(self): 
        # [Employee] Msg 1: File only
        self.auth_employee()
        data = {
            "applicationId": self.application.application_id,
            "fileUrl": "https://utfs.io/f/IiVMJL7J1Q98Pr3OF3uKRAsDCIS5jdvLBZw23T6fzthKQO0u",
            "fileName": "first_button.gif"
        }
        response = self.client.post(self.base_url, data, format="json")
        success_message = response.content.decode()
        message_id = success_message.split(" | ")[0].split(": ")[1]
        self.assertEqual(response.status_code, 200)

        # [Employer] Msg 2: Reply to Msg 1, Text and File
        self.auth_employer()
        data = {
            "content": "Inshallah",
            "applicationId": self.application.application_id,
            "replyToId": message_id,
            "fileUrl": "https://utfs.io/f/IiVMJL7J1Q98Pr3OF3uKRAsDCIS5jdvLBZw23T6fzthKQO0u",
            "fileName": "first_button.gif"
        }

        response = self.client.post(self.base_url, data, format="json")
        self.assertEqual(response.status_code, 200)


    # GET
    def get_messages(self): 
        self.auth_employer()
        data = {
            "applicationId": self.application.application_id
        }
        response = self.client.get(self.base_url, data)
        self.assertEqual(response.status_code, 200)
        
        overall_data = response.json()
        self.assertIsInstance(overall_data, list)

        for message_data in overall_data: 
            self.assertIsInstance(message_data, dict)
            self.assertEqual(len(message_data), 2)
            self.assertIn("message", message_data)
            self.assertIn("files", message_data)

            message = message_data["message"]
            verify_message_shape(message)

            message_files = message_data["files"]
            for message_file in message_files:
                verify_message_file_shape(message_file)


    # PATCH
    def patch_message(self): 
        # Update Msg 2
        self.auth_employer()
        data = {
            "applicationId": self.application.application_id,
            "newContent": "No Inshallah"
        }
        message_id = Message.objects.all()[1].message_id
        response = self.client.patch(f"{self.base_url}{message_id}/", data, format="json")
        self.assertEqual(response.status_code, 200)
        

 
    # DELETE
    def delete_message(self): 
        # Delete Msg 1
        self.auth_employee()
        message_id = Message.objects.all()[0].message_id
        response = self.client.delete(f"{self.base_url}{message_id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(MessageFile.objects.count(), 1)

        
