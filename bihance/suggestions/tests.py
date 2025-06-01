# Integration testing (models, serializers, utils, views)
# Negative test cases?

from django.test import TestCase
from rest_framework.test import APIClient
from utils.tests.objects import (
    create_employee_suggestion,
    get_employee,
    get_employer,
)
from utils.tests.utils import (
    verify_suggestion_comment_shape,
    verify_suggestion_shape,
    verify_suggestion_vote_shape,
    verify_user_shape,
)
from utils.utils import terminate_current_connections

from .models import Suggestion

terminate_current_connections()


class SuggestionsAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Performed once before all tests
        # Create test objects
        cls.employee = get_employee()
        cls.employer = get_employer()

        # This is suggestion 1
        create_employee_suggestion()

        # Base url for all users endpoint
        cls.base_url = "/api/suggestions/"

    def auth_employee(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.employee)

    def auth_employer(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.employer)

    # Main test function
    def test_all(self):
        self.create_suggestion()

        self.vote_suggestion()
        self.comment_suggestion()
        self.mark_implemented()

        self.get_suggestion()
        self.get_suggestions()
        self.get_leaderboards()

    # POST
    def create_suggestion(self):
        # Create suggestion 2 (note: 1 & 2 are both made by the employee)
        self.auth_employee()
        self.assertEqual(Suggestion.objects.count(), 1)

        data = {"title": "My Second Suggestion", "content": "LET ME UNDO MY CHOICES"}
        response = self.client.post(self.base_url, data, format="json")

        self.second_suggestion_id = (
            response.content.decode().split(": ")[1].replace(".", "")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Suggestion.objects.count(), 2)

    # POST vote
    def vote_suggestion(self):
        # Employee votes for suggestion 2
        self.auth_employee()
        response = self.client.post(f"{self.base_url}{self.second_suggestion_id}/vote/")
        self.assertEqual(response.status_code, 200)

        # Employer also votes for suggestion 2
        self.auth_employer()
        response = self.client.post(f"{self.base_url}{self.second_suggestion_id}/vote/")
        self.assertEqual(response.status_code, 200)

    # POST comment
    def comment_suggestion(self):
        # Employer comments on suggestion 2
        self.auth_employer()
        data = {"content": "Thats a great suggestion bro!"}
        response = self.client.post(
            f"{self.base_url}{self.second_suggestion_id}/comment/", data, format="json"
        )
        self.assertEqual(response.status_code, 200)

    # POST is_useful=True
    def mark_implemented(self):
        # Suggestion 2 is marked as implemented
        self.auth_employee()
        self.assertEqual(
            Suggestion.objects.get(suggestion_id=self.second_suggestion_id).is_useful,
            False,
        )
        response = self.client.post(
            f"{self.base_url}{self.second_suggestion_id}/mark_implemented/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Suggestion.objects.get(suggestion_id=self.second_suggestion_id).is_useful,
            True,
        )

    # GET single
    def get_suggestion(self):
        self.auth_employee()
        response = self.client.get(f"{self.base_url}{self.second_suggestion_id}/")
        self.assertEqual(response.status_code, 200)

        suggestion_info = response.json()
        self.assertIsInstance(suggestion_info, dict)

        # Validate author field
        self.assertIn("author", suggestion_info)
        author = suggestion_info["author"]
        verify_user_shape(author)

        # Validate suggestion field
        self.assertIn("suggestion", suggestion_info)
        suggestion = suggestion_info["suggestion"]
        verify_suggestion_shape(suggestion)
        self.assertEqual(suggestion["comment_count"], 1)
        self.assertEqual(suggestion["vote_count"], 2)

        # Validate votes field (if any)
        self.assertIn("votes", suggestion_info)
        votes = suggestion_info["votes"]
        if votes:
            for vote in votes:
                verify_suggestion_vote_shape(vote)

        # Validate comments field (if any)
        self.assertIn("comments", suggestion_info)
        comments = suggestion_info["comments"]
        if comments:
            for comment in comments:
                verify_suggestion_comment_shape(comment)

    # GET multiple
    def get_suggestions(self):
        self.auth_employee()
        query_params = {"searchQuery": "Suggestion", "sortBy": "most-voted"}
        response = self.client.get(self.base_url, query_params, format="json")
        self.assertEqual(response.status_code, 200)

        suggestions_info = response.json()
        self.assertIsInstance(suggestions_info, list)
        self.assertEqual(len(suggestions_info), 2)

        position = 1
        for suggestion_info in suggestions_info:
            self.assertIsInstance(suggestion_info, dict)

            # Validate author field
            self.assertIn("author", suggestion_info)
            author = suggestion_info["author"]
            verify_user_shape(author)

            # Validate votes field (if any)
            self.assertIn("votes", suggestion_info)
            votes = suggestion_info["votes"]
            if votes:
                for vote in votes:
                    verify_suggestion_vote_shape(vote)

            # Validate suggestion field
            self.assertIn("suggestion", suggestion_info)
            suggestion = suggestion_info["suggestion"]
            verify_suggestion_shape(suggestion)

            if position == 1:
                # We should see suggestion 2 first
                # Since it is the most voted
                self.assertEqual(suggestion["comment_count"], 1)
                self.assertEqual(suggestion["vote_count"], 2)
            else:
                # This is suggestion 1
                self.assertEqual(suggestion["comment_count"], 0)
                self.assertEqual(suggestion["vote_count"], 0)

            position += 1

    # GET leaderboards
    def get_leaderboards(self):
        self.auth_employee()
        query_params = {"sortBy": "most-implemented"}
        response = self.client.get(
            f"{self.base_url}leaderboards/", query_params, format="json"
        )
        self.assertEqual(response.status_code, 200)

        leaderboards_info = response.json()
        self.assertIsInstance(leaderboards_info, list)
        self.assertEqual(len(leaderboards_info), 2)

        position = 1
        for user_info in leaderboards_info:
            self.assertIsInstance(user_info, dict)
            verify_user_shape(user_info, extra_fields=["implemented_count"])

            if position == 1:
                # We should see employee first
                # Since it has one implemented suggestion, while employer has none
                self.assertEqual(user_info["employee"], True)
            else:
                # We should see the employer
                self.assertEqual(user_info["employee"], False)

            position += 1
