# Integration testing (models, serializers, utils, views)
# Negative test cases?

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from utils.tests.objects import (
    get_application,
    get_employee,
    get_employer,
    get_job,
)
from utils.tests.utils import (
    verify_file_shape,
    verify_group_member_shape,
    verify_group_message_shape,
)
from utils.utils import terminate_current_connections

from .models import Group, GroupMember, GroupMessage

terminate_current_connections()


class GroupsAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Performed once before all tests
        # Create test objects
        cls.employee = get_employee()
        cls.employer = get_employer()
        cls.job = get_job()
        cls.application = get_application()

        cls.base_url_group = "/api/groups/"
        cls.base_url_group_message = "/api/group-messages/"

    def auth_employee(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.employee)

    def auth_employer(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.employer)

    def test_all(self):
        # Interacting with Group and GroupMember
        self.create_group()
        self.update_group()
        self.get_available_members()

        # Interacting with GroupMessage and Files
        self.create_message()
        self.update_message()
        self.get_messages()
        self.delete_message()

    def create_group(self):
        self.auth_employee()
        data = {
            "bio": "My Sexy Group",
            "jobId": self.job.job_id,
            "userIds": [self.employee.id, self.employer.id],
        }
        response = self.client.post(self.base_url_group, data, format="json")
        self.group_id = response.content.decode().split(": ")[1].replace(".", "")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(GroupMember.objects.count(), 2)

        # Employee was the one who created the group
        # Hence, employee should be admin
        employee_member_role = GroupMember.objects.get(user_id=self.employee).role
        self.assertEqual(employee_member_role, "Admin")

    def update_group(self):
        self.auth_employee()
        data = {
            "bio": "My Super Sexy Group",
            "makeAdminIds": [self.employer.id],
            "stripAdminIds": [self.employee.id],
        }
        response = self.client.patch(
            f"{self.base_url_group}{self.group_id}/", data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(GroupMember.objects.count(), 2)

        # Now, admin has switched to employer
        employer_member_role = GroupMember.objects.get(user_id=self.employer).role
        self.assertEqual(employer_member_role, "Admin")

    def get_available_members(self):
        self.auth_employee()

        response = self.client.get(
            f"{self.base_url_group}{self.group_id}/available_members/"
        )
        self.assertEqual(response.status_code, 200)

    def create_message(self):
        self.auth_employee()
        data = {"content": "Hello Niggas", "groupId": self.group_id, "hasFile": False}

        self.assertEqual(GroupMessage.objects.count(), 0)
        response = self.client.post(self.base_url_group_message, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(GroupMessage.objects.count(), 1)

        success_message = response.content.decode()
        self.message_id = success_message.split(": ")[1].replace(".", "")

    def update_message(self):
        self.auth_employee()
        data = {"content": "Hello ALL Niggas", "groupId": self.group_id}

        response = self.client.patch(
            f"{self.base_url_group_message}{self.message_id}/", data, format="json"
        )
        self.assertEqual(response.status_code, 200)

    def get_messages(self):
        self.auth_employer()
        one_day_ago = timezone.now() - timedelta(days=1)
        query_params = {"since": one_day_ago.isoformat(), "groupId": self.group_id}
        response = self.client.get(
            self.base_url_group_message, query_params, format="json"
        )
        self.assertEqual(response.status_code, 200)

        messages_info = response.json()
        self.assertIsInstance(messages_info, list)
        self.assertEqual(len(messages_info), 1)

        for message_info in messages_info:
            self.assertIsInstance(message_info, dict)

            self.assertIn("message", message_info)
            message = message_info["message"]
            verify_group_message_shape(message)

            self.assertIn("sender", message_info)
            sender = message_info["sender"]
            verify_group_member_shape(sender)

            self.assertIn("reply_to_message", message_info)
            reply_to_message = message_info["reply_to_message"]
            if reply_to_message:
                verify_group_message_shape(reply_to_message)

            self.assertIn("file", message_info)
            message_file = message_info["file"]
            if message_file:
                verify_file_shape(message_file)

    def delete_message(self):
        self.auth_employee()

        # Note the rather "special" structure for the dynamic part of the url
        response = self.client.delete(
            f"{self.base_url_group_message}{self.message_id} || {self.group_id}/",
        )
        self.assertEqual(response.status_code, 200)

        # Since soft delete only
        self.assertEqual(GroupMessage.objects.count(), 1)
        self.assertEqual(
            GroupMessage.objects.first().content, "[This message has been deleted]"
        )
