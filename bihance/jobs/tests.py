# Integration testing (models, serializers, utils, views)
# Negative test cases? 

from applications.models import Job
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from utils.utils import terminate_current_connections
from utils.tests.objects import get_employee, get_employer, get_job, get_application
from utils.tests.utils import verify_application_shape, verify_job_shape, verify_job_requirement_shape, verify_file_shape


terminate_current_connections()

class ApplicationsAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Performed once before all tests
        # Create test objects
        cls.employee = get_employee()
        cls.employer = get_employer()

        # Job 1 (application attached to it)
        cls.job = get_job()
        cls.application = get_application()

        # Base url for all applications endpoint
        cls.base_url = '/api/jobs/'

        
    def auth_employee(self): 
        self.client = APIClient() 
        self.client.force_authenticate(user=self.employee)

    def auth_employer(self): 
        self.client = APIClient() 
        self.client.force_authenticate(user=self.employer)


    def test_all(self): 
        self.create_job() 
        self.get_all_jobs()
        self.get_single_job()
        self.modify_job()
        self.get_filtered_jobs()
        self.get_employer_jobs()
        self.delete_job()
    

    # POST
    def create_job(self): 
        # Job 2
        self.auth_employer()
        data = {
            "name": "Professional Clown",
            "startDate": timezone.now(),
            "description": "Must be able to transform into a tree, detect glitch entities.",
            "jobRequirements": ["funny", "thick-skinned", "frequently showers"]
        }

        response = self.client.post(self.base_url, data, format="json")
        self.assertEqual(response.status_code, 200)
        
        successText = response.content.decode()
        self.job2_id = successText.split(": ")[1].replace(".", "")


    # GET multiple
    def get_all_jobs(self): 
        self.auth_employee()
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)

        jobs = response.json()
        self.assertIsInstance(jobs, list)

        for job_info in jobs: 
            # Top level fields
            self.assertIn("job", job_info)
            self.assertIn("applications", job_info)
            self.assertIn("job_requirements", job_info)
            self.assertIn("file", job_info)

            # Nested fields
            job = job_info["job"]
            applications = job_info["applications"]
            job_requirements = job_info["job_requirements"]
            file = job_info["file"]

            verify_job_shape(job)
            
            if applications:
                for application in applications: 
                    verify_application_shape(application)

            if job_requirements:
                for job_requirement in job_requirements: 
                    verify_job_requirement_shape(job_requirement)

            if file: 
                verify_file_shape(file)
                
        
    # GET single 
    def get_single_job(self):
        # Get Job 1
        self.auth_employee()
        response = self.client.get(f"{self.base_url}{self.job.job_id}/")
        self.assertEqual(response.status_code, 200)

        job_info = response.json()
        self.assertIsInstance(job_info, dict)

        # Top level fields
        self.assertIn("job", job_info)
        self.assertIn("applications", job_info)
        self.assertIn("job_requirements", job_info)
        self.assertIn("file", job_info)

        # Nested fields
        job = job_info["job"]
        applications = job_info["applications"]
        job_requirements = job_info["job_requirements"]
        file = job_info["file"]

        verify_job_shape(job)

        if applications: 
            for application in applications: 
                verify_application_shape(application)

        if job_requirements:
            for job_requirement in job_requirements: 
                verify_job_requirement_shape(job_requirement)

        if file: 
            verify_file_shape(file)


    # PATCH 
    def modify_job(self): 
        # Modifying Job 1
        self.auth_employer()
        data = {
            "name": "HFT Trader",
            "payType": "Monthly",
            "salary": "12000"
        }

        response = self.client.patch(f"{self.base_url}{self.job.job_id}/", data, format="json")
        self.assertEqual(response.status_code, 200)


    # GET filtered 
    def get_filtered_jobs(self):
        self.auth_employee()
        response = self.client.get(f"{self.base_url}filtered/?search=funny")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

        
    # GET employer jobs 
    def get_employer_jobs(self):
        self.auth_employer()
        response = self.client.get(f"{self.base_url}employer_jobs/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)


    # DELETE
    def delete_job(self):
        # Delete Job 2
        self.auth_employer()
        response = self.client.delete(f"{self.base_url}{self.job2_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Job.objects.count(), 1)
        

    