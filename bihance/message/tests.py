# Integration testing (models, serializers, utils, views)
# Negative test cases?

from django.test import TestCase
from files.models import File
from rest_framework.test import APIClient
from utils.tests.objects import (
    get_application,
    get_employee,
    get_employer,
    get_job,
    get_message,
)
from utils.tests.utils import (
    verify_application_shape,
    verify_file_shape,
    verify_message_shape,
)
from utils.utils import terminate_current_connections

from .models import Message

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

        # [Msg 1]: From employee, text only
        cls.employee_message = get_message()

        # Base url for all messages endpoint
        cls.base_url = "/api/messages/"

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
        # [Msg 2]: Reply to Msg 1, from employer, text and file
        self.auth_employer()
        data = {
            "content": "Inshallah",
            "applicationId": self.application.application_id,
            "replyToId": self.employee_message.message_id,
            "hasFile": True,
        }
        response = self.client.post(self.base_url, data, format="json")
        self.assertEqual(response.status_code, 200)

        success_message = response.content.decode()
        message_id = success_message.split(": ")[1].replace(".", "")
        self.message_id = message_id

        data = {
            "fileKey": "YX7xA2cz6RDlzAiEhYyaEZD8247KIlgAHiNfeSLWX1y5Ju63",
            "fileUrl": "https://bhg1of7blh.ufs.sh/f/YX7xA2cz6RDlzAiEhYyaEZD8247KIlgAHiNfeSLWX1y5Ju63",
            "fileName": "catto",
            "fileType": "image/jpeg",
            "fileSize": 64755,
            "associatedType": "Message",
            "associatedObjectId": message_id,
        }
        response = self.client.post("/api/files/", data, format="json")
        self.assertEqual(response.status_code, 200)

    # GET
    def get_messages(self):
        self.auth_employer()
        data = {"applicationId": self.application.application_id}
        response = self.client.get(self.base_url, data)
        self.assertEqual(response.status_code, 200)

        messages = response.json()
        self.assertIsInstance(messages, list)
        self.assertEqual(len(messages), 2)

        for message_info in messages:
            # Top level fields
            self.assertIsInstance(message_info, dict)
            self.assertIn("message", message_info)
            self.assertIn("application", message_info)
            self.assertIn("reply_to_message", message_info)
            self.assertIn("file", message_info)

            message = message_info["message"]
            verify_message_shape(message)

            application = message_info["application"]
            verify_application_shape(application)

            reply_to_message = message_info["reply_to_message"]
            if reply_to_message:
                verify_message_shape(reply_to_message)

            file = message_info["file"]
            if file:
                verify_file_shape(file)

    # PATCH
    def patch_message(self):
        # Update Msg 2
        self.auth_employer()
        data = {
            "applicationId": self.application.application_id,
            "content": "No Inshallah",
        }
        message_id = Message.objects.all()[1].message_id
        response = self.client.patch(
            f"{self.base_url}{message_id}/", data, format="json"
        )
        self.assertEqual(response.status_code, 200)

    # DELETE
    def delete_message(self):
        # Delete Msg 2
        self.auth_employer()
        response = self.client.delete(f"{self.base_url}{self.message_id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(File.objects.count(), 0)
