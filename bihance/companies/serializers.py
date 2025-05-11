from .models import EmployerProfile, CompanyFollow
from applications.serializers import UserSerializer
from rest_framework import serializers


class EmployerProfileSerializer(serializers.ModelSerializer):
    employer = UserSerializer(source="employer_id", read_only=True)

    class Meta:
        model = EmployerProfile
        fields = [
            "company_id", "employer", "company_name", "company_website",
            "contact_name", "contact_role", "company_size", "industry",
            "talent_needs", "work_style", "hiring_timeline", "featured_partner", 
            "created_at", "updated_at", "image_url",
        ]


class CompanyFollowSerializer(serializers.ModelSerializer): 
    follower = UserSerializer(source="follower_id", read_only=True)
    company = EmployerProfileSerializer(source="company_id", read_only=True)

    class Meta: 
        model = CompanyFollow
        fields = [
            'follow_id', 'follower', 'company', 'created_at'
        ]


        