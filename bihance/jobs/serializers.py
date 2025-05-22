from applications.models import DurationType, JobType, PayType
from rest_framework import serializers
from utils.utils import detect_extra_fields

from .models import JobRequirement


# location (whats the diff with location-name?)
class JobCreateInputSerializer(serializers.Serializer):
    name = serializers.CharField()
    startDate = serializers.DateTimeField()
    endDate = serializers.DateTimeField(required=False)
    company = serializers.CharField(required=False)
    payType = serializers.ChoiceField(choices=PayType.choices, required=False)
    salary = serializers.FloatField(required=False)
    higherSalary = serializers.FloatField(required=False)
    duration = serializers.ChoiceField(choices=DurationType.choices, required=False)
    jobType = serializers.ChoiceField(choices=JobType.choices, required=False)
    startAge = serializers.IntegerField(required=False)
    endAge = serializers.IntegerField(required=False)
    gender = serializers.BooleanField(required=False)
    requirements = serializers.CharField(required=False)
    description = serializers.CharField()
    locationName = serializers.CharField(required=False)
    jobRequirements = serializers.ListField(
        required=False, child=serializers.CharField(), allow_empty=False
    )

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)

        if data.get("endDate") and data["endDate"] < data["startDate"]:
            raise serializers.ValidationError("End date must be after start date.")

        if (
            data.get("higherSalary")
            and data.get("salary")
            and data["higherSalary"] < data["salary"]
        ):
            raise serializers.ValidationError(
                "Higher salary cannot be less than salary."
            )

        if (
            data.get("startAge")
            and data.get("endAge")
            and data["endAge"] < data["startAge"]
        ):
            raise serializers.ValidationError(
                "End age must be greater than or equal to start age."
            )

        return data


class JobPartialUpdateInputSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    startDate = serializers.DateTimeField(required=False)
    endDate = serializers.DateTimeField(required=False)
    company = serializers.CharField(required=False)
    payType = serializers.ChoiceField(choices=PayType.choices, required=False)
    salary = serializers.FloatField(required=False)
    higherSalary = serializers.FloatField(required=False)
    duration = serializers.ChoiceField(choices=DurationType.choices, required=False)
    jobType = serializers.ChoiceField(choices=JobType.choices, required=False)
    startAge = serializers.IntegerField(required=False)
    endAge = serializers.IntegerField(required=False)
    gender = serializers.BooleanField(required=False)
    requirements = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    locationName = serializers.CharField(required=False)
    jobRequirements = serializers.ListField(
        required=False, child=serializers.CharField(), allow_empty=False
    )

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)

        if not data:
            raise serializers.ValidationError("At least one field must be modified.")

        if (
            data.get("startDate")
            and data.get("endDate")
            and data["endDate"] < data["startDate"]
        ):
            raise serializers.ValidationError("End date must be after start date.")

        if (
            data.get("higherSalary")
            and data.get("salary")
            and data["higherSalary"] < data["salary"]
        ):
            raise serializers.ValidationError(
                "Higher salary cannot be less than salary."
            )

        if (
            data.get("startAge")
            and data.get("endAge")
            and data["endAge"] < data["startAge"]
        ):
            raise serializers.ValidationError(
                "End age must be greater than or equal to start age."
            )

        return data


class JobFilteredInputSerializer(serializers.Serializer):
    jobType = serializers.ChoiceField(choices=JobType.choices, required=False)
    location = serializers.CharField(required=False)
    search = serializers.CharField(required=False)

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)

        if not data:
            raise serializers.ValidationError("At least one field must be modified.")

        return data


class JobRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRequirement
        fields = ["requirement_id", "name", "job_id"]
