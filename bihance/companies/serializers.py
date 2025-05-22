from rest_framework import serializers

from .models import CompanyFollow, EmployerProfile


class EmployerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerProfile
        fields = [
            "company_id",
            "employer_id",
            "company_name",
            "company_website",
            "contact_name",
            "contact_role",
            "company_size",
            "industry",
            "talent_needs",
            "work_style",
            "hiring_timeline",
            "featured_partner",
            "created_at",
            "updated_at",
        ]
        depth = 0


class CompanyFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyFollow
        fields = ["follow_id", "follower_id", "company_id", "created_at"]
        depth = 0
