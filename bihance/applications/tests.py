# Integration testing (models, serializers, utils, views)
# Negative test cases?

from django.test import TestCase
from rest_framework.test import APIClient
from utils.tests.objects import get_application, get_employee, get_employer, get_job
from utils.tests.utils import (
    verify_application_shape,
    verify_job_shape,
    verify_message_shape,
    verify_user_shape,
)
from utils.utils import terminate_current_connections

from .models import Application

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
        cls.base_url = "/api/applications/"

    def auth_employee(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.employee)

    def auth_employer(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.employer)

    # GET
    def test_get_applications(self):
        self.auth_employee()
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)

        applications = response.json()
        self.assertIsInstance(applications, list)

        for application_info in applications:
            self.assertIn("application", application_info)
            self.assertIn("job", application_info)
            self.assertIn("employee", application_info)
            self.assertIn("messages", application_info)

            application = application_info["application"]
            verify_application_shape(application)

            job = application_info["job"]
            verify_job_shape(job)

            employee = application_info["employee"]
            verify_user_shape(employee)

            messages = application_info["messages"]
            if messages:
                for message in messages:
                    verify_message_shape(message)

    # POST
    def test_create_application(self):
        # Delete current application
        self.auth_employee()
        self.application.delete()

        # Re-create the same application lol
        data = {
            "jobId": self.job.job_id,
            "employerId": self.employer.id,
        }
        response = self.client.post(self.base_url, data, format="json")
        self.assertEqual(response.status_code, 200)

    # PATCH
    def test_update_application_status(self):
        self.auth_employer()
        applicationId = Application.objects.first().application_id
        data = {
            "applicationStatus": 3,
        }
        response = self.client.patch(
            f"{self.base_url}{applicationId}/", data, format="json"
        )
        self.assertEqual(response.status_code, 200)

    # DELETE
    def test_delete_application(self):
        self.auth_employee()
        applicationId = Application.objects.first().application_id
        response = self.client.delete(f"{self.base_url}{applicationId}/")
        self.assertEqual(response.status_code, 200)
