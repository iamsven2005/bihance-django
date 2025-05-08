from .models import EmployerProfile, CompanyFollow
from applications.serializers import UserSerializer
from rest_framework import serializers


class EmployerProfileSerializer(serializers.ModelSerializer):
    employee = UserSerializer(source="employer_id", read_only=True)

    class Meta:
        model = EmployerProfile
        fields = [
            "company_id", "employee", "company_name", "company_website",
            "contact_name", "contact_role", "company_size", "industry",
            "talent_needs", "work_style", "hiring_timeline", "featured_partner", 
            "created_at", "updated_at", "image_url",
        ]


class CompanyFollowSerializer(serializers.ModelSerializer): 
    user = UserSerializer(source="user_id", read_only=True)
    company = EmployerProfileSerializer(source="company_id", read_only=True)

    class Meta: 
        model = CompanyFollow
        fields = [
            'follow_id', 'user', 'company', 'created_at'
        ]


        