from rest_framework import serializers
from utils.utils import detect_extra_fields

from .models import Application, Job, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "employee",
            "bio",
            "age",
            "created_at",
            "updated_at",
            "role",
            "location",
        ]
        depth = 0


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "job_id",
            "name",
            "employer_id",
            "start_date",
            "end_date",
            "salary",
            "higher_salary",
            "description",
            "requirements",
            "category",
            "posted_date",
            "start_age",
            "end_age",
            "gender",
            "location",
            "job_type",
            "location_name",
            "company",
            "duration",
            "pay_type",
        ]
        depth = 0


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "application_id",
            "job_id",
            "employee_id",
            "accept",
            "bio",
            "employee_review",
            "employer_review",
            "employer_id",
        ]
        depth = 0


class ApplicationListInputSerializer(serializers.Serializer):
    applicationStatus = serializers.IntegerField(required=False)
    userOnly = serializers.BooleanField(required=False)

    def validate_applicationStatus(self, value):
        num_value = int(value)
        if num_value < 0 or num_value > 4:
            raise serializers.ValidationError(
                "Application status can only be from 0 - 4."
            )

        return num_value

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)
        return data


class ApplicationCreateInputSerializer(serializers.Serializer):
    jobId = serializers.UUIDField()
    employerId = serializers.UUIDField()

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)

        job_id = data["jobId"]
        employer_id = data["employerId"]

        try:
            job = Job.objects.get(job_id=job_id)
        except Job.DoesNotExist:
            raise serializers.ValidationError("Job does not exist.")

        if job.employer_id.id != employer_id:
            raise serializers.ValidationError(
                "Job is not posted by the specified employer."
            )

        return data


class ApplicationPartialUpdateInputSerializer(serializers.Serializer):
    applicationStatus = serializers.IntegerField(required=False)
    bio = serializers.CharField(required=False)

    def validate_applicationStatus(self, value):
        num_value = int(value)
        if num_value not in [2, 3, 4]:
            raise serializers.ValidationError(
                "Application status can only be either 2 or 3 or 4."
            )

        return num_value

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)

        has_status = "applicationStatus" in data
        has_bio = "bio" in data

        # XOR
        if has_status ^ has_bio:
            return data
        raise serializers.ValidationError(
            "Can either update application status or application bio, but not both nor neither."
        )
