# Testing related utils
# .get_fields() automatically removes the excluded fields? 

from applications.serializers import UserSerializer, JobSerializer, ApplicationSerializer
from availabilities.serializers import AvailabilitySerializer
from companies.serializers import EmployerProfileSerializer, CompanyFollowSerializer
from message.serializers import MessageSerializer
from files.serializers import FileSerializer


# Verify shape of User JSON object
def verify_user_shape(user):
    expected_fields = UserSerializer().get_fields().keys()

    assert isinstance(user, dict), f"Expected user to be dict, got {type(user)} instead."
    for field in expected_fields:
        assert field in user, f"Missing field {field} in user."


# Verify shape of Job JSON object
def verify_job_shape(job):
    expected_fields = JobSerializer().get_fields().keys()
    
    assert isinstance(job, dict), f"Expected job to be dict, got {type(job)} instead."
    for field in expected_fields: 
        assert field in job, f"Missing field {field} in job."

        if field == "employer":
            employer = job[field]
            verify_user_shape(employer)


# Verify shape of Application JSON object
def verify_application_shape(application):
    expected_fields = ApplicationSerializer().get_fields().keys()

    assert isinstance(application, dict), f"Expected application to be dict, got {type(application)} instead."
    for field in expected_fields: 
        assert field in application, f"Missing field {field} in application."

        if field == "job":
            job = application[field]
            verify_job_shape(job)

        if field == "employee": 
            employee = application[field]
            verify_user_shape(employee)


# Verify shape of Availability JSON object 
def verify_availability_shape(availability): 
    expected_fields = AvailabilitySerializer().get_fields().keys()

    assert isinstance(availability, dict), f"Expected availability to be dict, got {type(availability)} instead."
    for field in expected_fields: 
        assert field in availability, f"Missing field {field} in availability."

        if field == "employee": 
            employee = availability[field]
            verify_user_shape(employee)


# Verify shape of EmployerProfile JSON object 
def verify_employer_profile_shape(employer_profile): 
    expected_fields = EmployerProfileSerializer().get_fields().keys()

    assert isinstance(employer_profile, dict), f"Expected employer profile to be dict, got {type(employer_profile)} instead."
    for field in expected_fields: 
        assert field in employer_profile, f"Missing field {field} in employer profile."

        if field == "employer": 
            employer = employer_profile[field]
            verify_user_shape(employer) 


# Verify shape of CompanyFollow JSON object 
def verify_company_follow_shape(company_follow): 
    expected_fields = CompanyFollowSerializer().get_fields().keys()

    assert isinstance(company_follow, dict), f"Expected company follow to be dict, got {type(company_follow)} instead."
    for field in expected_fields: 
        assert field in company_follow, f"Missing field {field} in company follow."

        if field == "follower": 
            follower = company_follow[field]
            verify_user_shape(follower) 

        if field == "company": 
            company = company_follow[field]
            verify_employer_profile_shape(company)
    

# Verify shape of Message JSON object
def verify_message_shape(message):
    expected_fields = MessageSerializer().get_fields().keys()

    assert isinstance(message, dict), f"Expected message to be dict, got {type(message)} instead."
    for field in expected_fields: 
        assert field in message, f"Missing field {field} in message."

        if field == "application": 
            application = message[field]
            verify_application_shape(application)

        if field == "sender": 
            sender = message[field]
            verify_user_shape(sender)

        if field == "reply_to_message" and message[field]: # Ensure value is not None first
            reply_to_message = message[field]
            verify_message_shape(reply_to_message)
    

# Verify shape of File JSON object 
def verify_file_shape(file): 
    expected_fields = FileSerializer().get_fields().keys()

    assert isinstance(file, dict), f"Expected file to be dict, got {type(file)} instead."
    for field in expected_fields:
        assert field in file, f"Missing field {field} in file."


