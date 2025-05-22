# Non-testing related utils

from applications.models import Application, User
from django.db import connection
from rest_framework import serializers
from rest_framework.exceptions import NotFound


def check_is_employee(employee_id): 
    employee = User.objects.get(id=employee_id)
    return employee.employee

def check_is_employer(employer_id): 
    employer = User.objects.get(id=employer_id)
    return not employer.employee


def terminate_current_connections(): 
    cursor = connection.cursor()
    database_name = 'test_Development'
    cursor.execute(
        "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity "
        "WHERE pg_stat_activity.datname = %s AND pid <> pg_backend_pid();", [database_name])
    

# Both args are dictionaries
def detect_extra_fields(initial_data, serializer_fields): 
    extra_fields = set(initial_data.keys()) - set(serializer_fields.keys())
    if extra_fields: 
        raise serializers.ValidationError(f"Got unknown fields: {extra_fields}")
    

def get_user_and_application(user_id, application_id):
    # Try to retrieve the user record 
    try: 
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise NotFound("No user corresponding to the message.")
    
    # Try to retrive the application record 
    try: 
        application = Application.objects.get(application_id=application_id)
    except Application.DoesNotExist: 
        raise NotFound("No application corresponding to the message.")
    
    return (user, application)


def validate_user_in_application(user, application): 
    if application.employee_id != user and application.employer_id != user.id: 
        return False
    else: 
        return True
    

# Remap keys in the dictionary of validated inputs 
# From input_fields to model_fields
# Usually for POST or PATCH
def remap_keys(input_dict, mapping): 
    result = {}
    for input_field, value in input_dict.items(): 
        model_field = mapping.get(input_field)
        if model_field: 
            # Ignore the keys that do not correspond to a model_field
            result[model_field] = value

    return result