from applications.models import Application, User
from rest_framework import serializers


def check_new_ids(new_ids, associated_job):
    for user_id in new_ids:
        user = User.objects.get(id=user_id)
        if user.employee:
            try:
                Application.objects.get(job_id=associated_job, employee_id=user)
            except Application.DoesNotExist:
                raise Exception("Employee is not an applicant for the job.")
        else:
            if associated_job.employer_id != user:
                raise Exception("Employer is not poster for the job.")


def validate_no_duplicates(value, label):
    if len(set(value)) < len(value):
        raise serializers.ValidationError(f"Each user can only appear once in {label}.")
    return value


def uuid_to_string(uuid_list):
    if uuid_list:
        return set(str(uuid) for uuid in uuid_list)
    else:
        return None
