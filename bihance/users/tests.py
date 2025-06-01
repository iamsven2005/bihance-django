# Integration testing (models, serializers, utils, views)
# Negative test cases?
from django.test import TestCase
from rest_framework.test import APIClient
from utils.tests.objects import (
    create_employee_interests,
    create_employee_skills,
    get_employee,
)
from utils.tests.utils import (
    verify_interest_shape,
    verify_skill_shape,
    verify_user_shape,
)
from utils.utils import terminate_current_connections

from .models import Skill

terminate_current_connections()


class UsersAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Performed once before all tests
        # Create test objects
        cls.employee = get_employee()

        create_employee_skills()
        create_employee_interests()

        # Base url for all users endpoint
        cls.base_url = "/api/users/"

    def setUp(self):
        # Called before each test
        self.client = APIClient()
        self.client.force_authenticate(user=self.employee)

    # Main test function
    def test_all(self):
        self.get_user()
        self.update_user()
        self.toggle_user_role()
        self.search_users()
        self.search_skills()

    # GET single
    def get_user(self):
        response = self.client.get(f"{self.base_url}{self.employee.id}/")
        self.assertEqual(response.status_code, 200)

        user_info = response.json()
        self.assertIsInstance(user_info, dict)

        # Field validation
        self.assertIn("user", user_info)
        user = user_info["user"]
        verify_user_shape(user)

        self.assertIn("skills", user_info)
        skills = user_info["skills"]
        if skills:
            for skill in skills:
                verify_skill_shape(skill)

        self.assertIn("interests", user_info)
        interests = user_info["interests"]
        if interests:
            for interest in interests:
                verify_interest_shape(interest)

    # PATCH - option 1
    def update_user(self):
        data = {
            "firstName": "John",
            "lastName": "Doe",
            # Skill object
            "skills": [{"name": "React"}, {"name": "SQL"}],
        }
        response = self.client.patch(
            f"{self.base_url}{self.employee.id}/", data, format="json"
        )

        self.assertEqual(response.status_code, 200)

        self.employee.refresh_from_db()
        self.assertEqual(self.employee.first_name, "John")
        self.assertEqual(self.employee.last_name, "Doe")
        self.assertEqual(Skill.objects.count(), 2)

    # PATCH - option 2
    def toggle_user_role(self):
        data = {"toggleRole": True}
        response = self.client.patch(
            f"{self.base_url}{self.employee.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, 200)

        self.employee.refresh_from_db()
        self.assertEqual(self.employee.employee, False)

    # GET multiple -> users/search/
    def search_users(self):
        # If query_params contains mapping types (eg: list, tuple, dict)
        # We always try to conver to List[str] format
        # For expected request.query_params behaviour
        # Else (for eg: List[dict]), then request.query_params sees List[str ver of dict]
        query_params = {
            "name": "J",
            "page": 1,
            "limit": 2,
            # Skill names only
            "skills": ["React", "SQL"],
        }

        response = self.client.get(
            f"{self.base_url}search/", query_params, format="json"
        )
        self.assertEqual(response.status_code, 200)

        users_info = response.json()
        self.assertIsInstance(users_info, dict)

        # Field validation
        self.assertIn("users", users_info)
        users = users_info["users"]
        for user_info in users:
            self.assertIsInstance(user_info, dict)

            # Field validation
            self.assertIn("user", user_info)
            user = user_info["user"]
            verify_user_shape(user)

            self.assertIn("skills", user_info)
            skills = user_info["skills"]
            if skills:
                for skill in skills:
                    verify_skill_shape(skill)

            self.assertIn("interests", user_info)
            interests = user_info["interests"]
            if interests:
                for interest in interests:
                    verify_interest_shape(interest)

        self.assertIn("totalUsers", users_info)
        total_users = users_info["totalUsers"]
        self.assertEqual(total_users, 1)

        self.assertIn("totalPages", users_info)
        total_pages = users_info["totalPages"]
        self.assertEqual(total_pages, 1)

    # GET multiple -> users/skills
    def search_skills(self):
        response = self.client.get(f"{self.base_url}skills/")
        self.assertEqual(response.status_code, 200)

        skill_groups = response.json()
        self.assertIsInstance(skill_groups, list)

        # Employee has been updated to possess two different skills
        # Hence, there should be 2 skill groups
        self.assertEqual(len(skill_groups), 2)

        for skill_group in skill_groups:
            self.assertIn("name", skill_group)
            self.assertIn("count", skill_group)
