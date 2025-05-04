# Integration testing (models, serializers, utils, views)
# Negative test cases? 

from .models import Timings
from applications.models import User
from datetime import timedelta
from django.db import connection
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient


# Close all connections to test database
# To allow tests to run (kinda) smoothly
cursor = connection.cursor()
database_name = 'test_Development'
cursor.execute(
    "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity "
    "WHERE pg_stat_activity.datname = %s AND pid <> pg_backend_pid();", [database_name])


class AvailabilitiesAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Performed once before all tests 
        # Create test employee 
        cls.employee = User.objects.create(
            id="user_2wGGKihK36mWtgSzXpMoPYyLulX",
            email="employee@gmail.com",
            employee=True
        )

        # Create availability 
        cls.employee_availability = Timings.objects.create(
            start_time= timezone.now(), 
            end_time= timezone.now() + timedelta(days=69),
            employee_id=cls.employee,
            title="daddy"
        )

        # Base url for all availabilities endpoint
        cls.base_url = '/api/availabilities/'

    def setUp(self): 
        # Performed once before each test
        self.client = APIClient()
        self.client.force_authenticate(user=self.employee)


    # POST 
    def test_create_availability(self):
        # Create another valid availability 
        startTime = timezone.now() + timedelta(days=70)
        endTime = startTime + timedelta(days=7)
        data = {
            "startTime": startTime,
            "endTime": endTime,
            "title": "mommy"
        }
        response = self.client.post(self.base_url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Timings.objects.count(), 2)


    # GET 
    def test_get_availabilities(self): 
        response = self.client.get(self.base_url) 
        self.assertEqual(response.status_code, 200)

        availabilities = response.json()
        self.assertIsInstance(availabilities, list)

        # Verify the shape of availabilities -> a list of dictonaries
        # Where each dictionary follows the serialized structure
        for availability in availabilities: 
            self.assertIsInstance(availability, dict)

            # Top-level fields
            self.assertIn('time_id', availability)
            self.assertIn('start_time', availability)
            self.assertIn('end_time', availability)
            self.assertIn('title', availability)

            # Nested 'employee' dictionary
            employee = availability['employee']
            self.assertIsInstance(employee, dict)
            self.assertIn('id', employee)
            self.assertIn('first_name', employee)
            self.assertIn('last_name', employee)
            self.assertIn('email', employee)
        
    
    # DELETE 
    def test_delete_availabilities(self):
        availability_id = Timings.objects.all().first().time_id + "/"
        response = self.client.delete(f"{self.base_url}{availability_id}")

        # Changes from each test case, does NOT seem to be propogated
        # Hence, the count after delete is 0, NOT 1
        self.assertEqual(Timings.objects.count(), 0)
        self.assertEqual(response.status_code, 200)


