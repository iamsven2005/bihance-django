from rest_framework import serializers
from .models import Application, Job, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'email', 'image_url', 'phone',
            'employee', 'bio', 'age', 'created_at', 'updated_at', 'role', 'location'
        ]


class JobSerializer(serializers.ModelSerializer):
    employer = UserSerializer(source='employer_id', read_only=True)

    class Meta:
        model = Job
        fields = [
            'job_id', 'name', 'employer', 'start_date', 'end_date', 'salary', 'higher_salary',
            'description', 'requirements', 'posted_date', 'photo_url', 'start_age', 'end_age',
            'gender', 'location', 'job_type', 'location_name', 'company', 'duration', 'pay_type'
        ]


class ApplicationSerializer(serializers.ModelSerializer):
    job = JobSerializer(source='job_id', read_only=True)
    employee = UserSerializer(source='employee_id', read_only=True)

    class Meta:
        model = Application
        fields = [
            'application_id', 'job', 'employee', 'accept',
            'bio', 'employee_review', 'employer_review', 'employer_id'
        ]