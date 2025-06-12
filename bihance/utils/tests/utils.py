# Testing related utils
# Testing is done in DEV, so assertions are enabled

from applications.serializers import (
    ApplicationSerializer,
    JobSerializer,
    UserSerializer,
)
from availabilities.serializers import AvailabilitySerializer
from companies.serializers import CompanyFollowSerializer, EmployerProfileSerializer
from files.serializers import FileSerializer
from groups.serializers import (
    GroupMemberSerializer,
    GroupMessageSerializer,
    GroupSerializer,
)
from jobs.serializers import JobRequirementSerializer
from message.serializers import MessageSerializer
from suggestions.serializers import (
    SuggestionCommentSerializer,
    SuggestionSerializer,
    SuggestionVoteSerializer,
)
from users.serializers import InterestSerializer, SkillSerializer

# Mapping of object types to their serializers
object_type_to_serializer_mapping = {
    "user": UserSerializer,
    "job": JobSerializer,
    "job_requirement": JobRequirementSerializer,
    "application": ApplicationSerializer,
    "availability": AvailabilitySerializer,
    "employer_profile": EmployerProfileSerializer,
    "company_follow": CompanyFollowSerializer,
    "message": MessageSerializer,
    "file": FileSerializer,
    "skill": SkillSerializer,
    "interest": InterestSerializer,
    "suggestion": SuggestionSerializer,
    "suggestion_comment": SuggestionCommentSerializer,
    "suggestion_vote": SuggestionVoteSerializer,
    "group": GroupSerializer,
    "group_member": GroupMemberSerializer,
    "group_message": GroupMessageSerializer,
}


# Verify shape of JSON object
# Extra_fields -> those NOT from the ModelSerializer
def verify_object_shape(object, object_type, extra_fields=[]):
    object_serializer = object_type_to_serializer_mapping[object_type]
    expected_fields = object_serializer().get_fields().keys()
    if extra_fields:
        expected_fields = list(expected_fields)
        expected_fields.extend(extra_fields)

    assert len(object.keys()) == len(expected_fields), (
        f"{object_type} does not contain expected number of fields."
    )

    assert isinstance(object, dict), (
        f"Expected {object_type} to be dict, got {type(object)} instead."
    )

    for field in expected_fields:
        assert field in object, f"Missing field {field} in {object_type}."


# Verify shape of User JSON object
def verify_user_shape(user, extra_fields=[]):
    verify_object_shape(user, "user", extra_fields)


# Verify shape of Job JSON object
def verify_job_shape(job, extra_fields=[]):
    verify_object_shape(job, "job", extra_fields)


# Verify shape of Job Requirement JSON object
def verify_job_requirement_shape(job_requirement, extra_fields=[]):
    verify_object_shape(job_requirement, "job_requirement", extra_fields)


# Verify shape of Application JSON object
def verify_application_shape(application, extra_fields=[]):
    verify_object_shape(application, "application", extra_fields)


# Verify shape of Availability JSON object
def verify_availability_shape(availability, extra_fields=[]):
    verify_object_shape(availability, "availability", extra_fields)


# Verify shape of EmployerProfile JSON object
def verify_employer_profile_shape(employer_profile, extra_fields=[]):
    verify_object_shape(employer_profile, "employer_profile", extra_fields)


# Verify shape of CompanyFollow JSON object
def verify_company_follow_shape(company_follow, extra_fields=[]):
    verify_object_shape(company_follow, "company_follow", extra_fields)


# Verify shape of Message JSON object
def verify_message_shape(message, extra_fields=[]):
    verify_object_shape(message, "message", extra_fields)


# Verify shape of File JSON object
def verify_file_shape(file, extra_fields=[]):
    verify_object_shape(file, "file", extra_fields)


# Verify shape of Skill JSON object
def verify_skill_shape(skill, extra_fields=[]):
    verify_object_shape(skill, "skill", extra_fields)


# Verify shape of Interest JSON object
def verify_interest_shape(interest, extra_fields=[]):
    verify_object_shape(interest, "interest", extra_fields)


# Verify shape of Suggestion JSON object
def verify_suggestion_shape(suggestion, extra_fields=[]):
    verify_object_shape(suggestion, "suggestion", extra_fields)


# Verify shape of SuggestionComment JSON object
def verify_suggestion_comment_shape(suggestion_comment, extra_fields=[]):
    verify_object_shape(suggestion_comment, "suggestion_comment", extra_fields)


# Verify shape of SuggestionVote JSON object
def verify_suggestion_vote_shape(suggestion_vote, extra_fields=[]):
    verify_object_shape(suggestion_vote, "suggestion_vote", extra_fields)


# Verify shape of Group JSON object
def verify_group_shape(group, extra_fields=[]):
    verify_object_shape(group, "group", extra_fields)


# Verify shape of Group Member JSON object
def verify_group_member_shape(group_member, extra_fields=[]):
    verify_object_shape(group_member, "group_member", extra_fields)


# Verify shape of Group Message JSON object
def verify_group_message_shape(group_message, extra_fields=[]):
    verify_object_shape(group_message, "group_message", extra_fields)
