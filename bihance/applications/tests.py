# Integration testing (models, serializers, utils, views)
# Negative test cases? 

from .models import Application
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

        # Base url for all applications endpoint
        cls.base_url = '/api/applications/'
        
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

        # Verify the shape of applications -> a list of dictonaries
        # Where each dictionary follows the serialized structure
        for application in applications: 
            self.assertIsInstance(application, dict)

            # Top-level fields
            self.assertIn('application_id', application)
            self.assertIn('job', application)
            self.assertIn('employee', application)
            self.assertIn('accept', application)
            self.assertIn('bio', application)
            self.assertIn('employee_review', application)
            self.assertIn('employer_review', application)
            self.assertIn('employer_id', application)

            # Nested 'job' dictionary
            job = application['job']
            self.assertIsInstance(job, dict)
            self.assertIn('job_id', job)
            self.assertIn('name', job)
            self.assertIn('employer', job)

            # Nested 'employer' dictionary inside job
            employer = job['employer']
            self.assertIsInstance(employer, dict)
            self.assertIn('id', employer)
            self.assertIn('first_name', employer)
            self.assertIn('last_name', employer)
            self.assertIn('email', employer)

            # Nested 'employee' dictionary
            employee = application['employee']
            self.assertIsInstance(employee, dict)
            self.assertIn('id', employee)
            self.assertIn('first_name', employee)
            self.assertIn('last_name', employee)
            self.assertIn('email', employee)
        

    # POST
    def test_create_application(self):
        # Delete current application 
        self.auth_employee()
        self.application.delete()

        # Re-create the same application lol 
        data = {
            "jobId": "cma20egbu0007145n7evi1u6d",
            "employerId": "user_2w9owsASS9O50XlIGdFubAjr8x0"
        }
        response = self.client.post(self.base_url, data, format='json')
        self.assertEqual(response.status_code, 200)


    # PATCH
    def test_update_application_status(self): 
        self.auth_employer()
        applicationId = Application.objects.first().application_id
        data = {
            "newStatus": 3,
        }
        response = self.client.patch(f'{self.base_url}{applicationId + "/"}', data, format='json')
        self.assertEqual(response.status_code, 200)


    # DELETE
    def test_delete_application(self):
        self.auth_employee()
        applicationId = Application.objects.first().application_id + "/"
        response = self.client.delete(f'{self.base_url}{applicationId}')
        self.assertEqual(response.status_code, 200)


