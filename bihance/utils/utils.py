from applications.models import User


def check_is_employee(employee_id): 
    employee = User.objects.get(id=employee_id)
    return employee.employee

def check_is_employer(employer_id): 
    employer = User.objects.get(id=employer_id)
    return not employer.employee


