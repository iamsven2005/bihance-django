# Integration testing (models, serializers, utils, views)
# Negative test cases?

from django.test import TestCase
from rest_framework.test import APIClient
from utils.tests.objects import (
    get_application,
    get_employee,
    get_employer,
    get_job,
)
from utils.utils import terminate_current_connections

from .models import Group, GroupMember

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

        # Base url for all messages endpoint
        cls.base_url = "/api/groups/"

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
        # ...

    def create_group(self):
        self.auth_employee()
        data = {
            "bio": "My Sexy Group",
            "jobId": self.job.job_id,
            "userIds": [self.employee.id, self.employer.id],
        }
        response = self.client.post(self.base_url, data, format="json")
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
            f"{self.base_url}{self.group_id}/", data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(GroupMember.objects.count(), 2)

        # Now, admin has switched to employer
        employer_member_role = GroupMember.objects.get(user_id=self.employer).role
        self.assertEqual(employer_member_role, "Admin")

    def get_available_members(self):
        self.auth_employee()

        response = self.client.get(f"{self.base_url}{self.group_id}/available_members/")
        self.assertEqual(response.status_code, 200)
