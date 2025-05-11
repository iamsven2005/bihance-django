# Integration testing (models, serializers, utils, views)
# Negative test cases? 

from .models import EmployerProfile
from django.test import TestCase
from rest_framework.test import APIClient
from tests.objects import get_employee, get_employer, get_job
from tests.utils import verify_employer_profile_shape, verify_job_shape
from utils.utils import terminate_current_connections


terminate_current_connections()

class CompaniesAPITest(TestCase): 
    @classmethod
    def setUpTestData(cls):
        # Performed once before all tests 
        # Create test objects 
        cls.employee = get_employee()        
        cls.employer = get_employer()
        cls.job = get_job()
        cls.employer_profile = EmployerProfile.objects.create(
            employer_id=cls.employer,
            company_name="Mashallah PTE LTD."
        )

        # Base url for all requests to this API
        cls.base_url = "/api/companies/"
        
    def setUp(self):
        # Performed once before each test
        self.client = APIClient() 
        self.client.force_authenticate(user=self.employee)


    # GET multiple companies
    def test_get_companies(self): 
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)

        companies = response.json()
        for company in companies: 
            verify_employer_profile_shape(company)


    # GET single company
    def test_get_company(self): 
        response = self.client.get(f"{self.base_url}{self.employer_profile.company_id}/")
        self.assertEqual(response.status_code, 200)

        company_and_jobs = response.json()
        self.assertIsInstance(company_and_jobs, dict)

        # Top level fields
        self.assertIn("company", company_and_jobs)
        self.assertIn("jobs", company_and_jobs)
        
        # Nested fields 
        company_info = company_and_jobs["company"]
        verify_employer_profile_shape(company_info)
        
        jobs_info = company_and_jobs["jobs"]
        for job_info in jobs_info: 
            verify_job_shape(job_info)


    # Combined testing
    def test_follow_features(self):
        self.follow_company()
        self.unfollow_company()
        self.check_is_following()
        self.check_followers_count()

    # POST follow
    def follow_company(self):
        response = self.client.post(f"{self.base_url}{self.employer_profile.company_id}/follow/")
        self.assertEqual(response.status_code, 200)

        follow_status = response.content.decode()
        self.assertIn("followed", follow_status)

    # POST unfollow
    def unfollow_company(self): 
        response = self.client.post(f"{self.base_url}{self.employer_profile.company_id}/follow/")
        self.assertEqual(response.status_code, 200)

        follow_status = response.content.decode()
        self.assertIn("unfollowed", follow_status)


    # GET is_following
    def check_is_following(self): 
        response = self.client.get(f"{self.base_url}{self.employer_profile.company_id}/is_following/")
        self.assertEqual(response.status_code, 200)

        is_following = response.content.decode()
        self.assertIn(f"{False}", is_following)


    # GET company followers_count
    def check_followers_count(self):
        response = self.client.get(f"{self.base_url}{self.employer_profile.company_id}/followers/")
        self.assertEqual(response.status_code, 200)

        followers_count = response.content.decode()
        self.assertIn("0", followers_count)

    
