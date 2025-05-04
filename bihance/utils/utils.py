from applications.models import User
from django.db import connection


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
    

    