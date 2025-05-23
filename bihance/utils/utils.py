# Non-testing related utils

from django.db import connection
from rest_framework import serializers


def is_employee(user):
    return user.employee


def is_employer(user):
    return not user.employee


def is_employee_in_application(employee, application):
    return application.employee_id == employee


def is_employer_in_application(employer, application):
    return application.employer_id == employer


def terminate_current_connections():
    cursor = connection.cursor()
    database_name = "test_Development"
    cursor.execute(
        "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity "
        "WHERE pg_stat_activity.datname = %s AND pid <> pg_backend_pid();",
        [database_name],
    )


# Both args are dictionaries
def detect_extra_fields(initial_data, serializer_fields):
    extra_fields = set(initial_data.keys()) - set(serializer_fields.keys())
    if extra_fields:
        raise serializers.ValidationError(f"Got unknown fields: {extra_fields}")


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
