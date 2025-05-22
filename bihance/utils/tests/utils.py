# Testing related utils

from applications.serializers import (
    ApplicationSerializer,
    JobSerializer,
    UserSerializer,
)
from availabilities.serializers import AvailabilitySerializer
from companies.serializers import CompanyFollowSerializer, EmployerProfileSerializer
from files.serializers import FileSerializer
from jobs.serializers import JobRequirementSerializer
from message.serializers import MessageSerializer


# Verify shape of User JSON object
def verify_user_shape(user):
    expected_fields = UserSerializer().get_fields().keys()

    assert isinstance(user, dict), (
        f"Expected user to be dict, got {type(user)} instead."
    )
    for field in expected_fields:
        assert field in user, f"Missing field {field} in user."


# Verify shape of Job JSON object
def verify_job_shape(job):
    expected_fields = JobSerializer().get_fields().keys()

    assert isinstance(job, dict), f"Expected job to be dict, got {type(job)} instead."
    for field in expected_fields:
        assert field in job, f"Missing field {field} in job."


# Verify shape of Job Requirement JSON object
def verify_job_requirement_shape(job_requirement):
    expected_fields = JobRequirementSerializer().get_fields().keys()

    assert isinstance(job_requirement, dict), (
        f"Expected job requirement to be dict, got {type(job_requirement)} instead."
    )
    for field in expected_fields:
        assert field in job_requirement, f"Missing field {field} in job_requirement."


# Verify shape of Application JSON object
def verify_application_shape(application):
    expected_fields = ApplicationSerializer().get_fields().keys()

    assert isinstance(application, dict), (
        f"Expected application to be dict, got {type(application)} instead."
    )
    for field in expected_fields:
        assert field in application, f"Missing field {field} in application."


# Verify shape of Availability JSON object
def verify_availability_shape(availability):
    expected_fields = AvailabilitySerializer().get_fields().keys()

    assert isinstance(availability, dict), (
        f"Expected availability to be dict, got {type(availability)} instead."
    )
    for field in expected_fields:
        assert field in availability, f"Missing field {field} in availability."


# Verify shape of EmployerProfile JSON object
def verify_employer_profile_shape(employer_profile):
    expected_fields = EmployerProfileSerializer().get_fields().keys()

    assert isinstance(employer_profile, dict), (
        f"Expected employer profile to be dict, got {type(employer_profile)} instead."
    )
    for field in expected_fields:
        assert field in employer_profile, f"Missing field {field} in employer profile."


# Verify shape of CompanyFollow JSON object
def verify_company_follow_shape(company_follow):
    expected_fields = CompanyFollowSerializer().get_fields().keys()

    assert isinstance(company_follow, dict), (
        f"Expected company follow to be dict, got {type(company_follow)} instead."
    )
    for field in expected_fields:
        assert field in company_follow, f"Missing field {field} in company follow."


# Verify shape of Message JSON object
def verify_message_shape(message):
    expected_fields = MessageSerializer().get_fields().keys()

    assert isinstance(message, dict), (
        f"Expected message to be dict, got {type(message)} instead."
    )
    for field in expected_fields:
        assert field in message, f"Missing field {field} in message."


# Verify shape of File JSON object
def verify_file_shape(file):
    expected_fields = FileSerializer().get_fields().keys()

    assert isinstance(file, dict), (
        f"Expected file to be dict, got {type(file)} instead."
    )
    for field in expected_fields:
        assert field in file, f"Missing field {field} in file."
