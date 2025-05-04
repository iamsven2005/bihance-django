# Integration testing (models, serializers, utils, views)
# Negative test cases? 

from .models import Message, MessageFile
from django.test import TestCase
from rest_framework.test import APIClient
from tests.objects import get_employee, get_employer, get_job, get_application
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
            "applicationId": self.application.application_id,
        }
        response = self.client.get(self.base_url, data)
        self.assertEqual(response.status_code, 200)
        
        combined_data = response.json()
        self.assertIsInstance(combined_data, dict)
        self.assertIn("messages", combined_data)
        self.assertIn("message_files", combined_data)

        messages = combined_data["messages"]
        message_files = combined_data["message_files"]
        self.assertEqual(len(messages), len(message_files))

        for message in messages: 
            self.assertIsInstance(message, dict)

            # Top level fields 
            self.assertIn("message_id", message)
            self.assertIn("content", message)
            self.assertIn("date", message)
            self.assertIn("is_edited", message)
            self.assertIn("is_deleted", message)
            self.assertIn("last_edited_at", message)

            # Nested fields
            application = message["application"]
            sender = message["sender"]
            reply_to_message = message["reply_to_message"]
            self.assertIsInstance(application, dict)
            self.assertIsInstance(sender, dict)
            self.assertIsInstance(reply_to_message, dict | None)

        for message_file in message_files:
            self.assertIsInstance(message_file, dict)
            # <Will update later>
            pass


    # PATCH
    def patch_message(self): 
        # Update Msg 2
        self.auth_employer()
        data = {
            "applicationId": self.application.application_id,
            "newContent": "No Inshallah"
        }
        message_id = Message.objects.all()[1].message_id + "/"
        response = self.client.patch(f"{self.base_url}{message_id}", data, format="json")
        self.assertEqual(response.status_code, 200)

 
    # DELETE
    def delete_message(self): 
        # Delete Msg 1
        self.auth_employee()
        message_id = Message.objects.all()[0].message_id + "/"
        response = self.client.delete(f"{self.base_url}{message_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(MessageFile.objects.count(), 1)

        
