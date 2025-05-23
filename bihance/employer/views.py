from companies.models import EmployerProfile
from django.http import HttpResponse
from rest_framework import permissions, viewsets
from utils.utils import is_employer, remap_keys

from .serializers import (
    EmployerCreateInputSerializer,
    EmployerPartialUpdateInputSerializer,
)
from .utils import is_employer_in_company


class EmployerViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    input_field_to_model_field_mapping = {
        "companyName": "company_name",
        "companyWebsite": "company_website",
        "contactName": "contact_name",
        "contactRole": "contact_role",
        "companySize": "company_size",
        "industry": "industry",
        "talentNeeds": "talent_needs",
        "workStyle": "work_style",
        "hiringTimeline": "hiring_timeline",
        "featuredPartner": "featured_partner",
    }

    # POST -> employer/
    def create(self, request):
        # User verification
        if not is_employer(request.user):
            return HttpResponse("User must be an employer.", status=400)

        # Input validation
        serializer = EmployerCreateInputSerializer(data=request.data)
        if not serializer.is_valid():
            return HttpResponse(serializer.errors, status=400)

        validated_data = serializer.validated_data
        processed_data = remap_keys(
            validated_data, self.input_field_to_model_field_mapping
        )

        # Check if the employer profile exists already
        try:
            # UNIQUE constraint
            EmployerProfile.objects.get(
                employer_id=request.user,
                company_name=processed_data["company_name"],
                company_website=processed_data["company_website"],
            )
            return HttpResponse("Employer profile exists already.", status=400)

        except EmployerProfile.DoesNotExist:
            pass

        # Create the new employer profile
        processed_data["employer_id"] = request.user
        employer_company = EmployerProfile.objects.create(**processed_data)
        company_id = employer_company.company_id

        return HttpResponse(
            f"Employer profile successfully created with company id: {company_id}.",
            status=200,
        )

    # PATCH -> employer/:company_id
    def partial_update(self, request, pk=None):
        # Try to retrieve the company record
        try:
            company = EmployerProfile.objects.get(company_id=pk)
        except EmployerProfile.DoesNotExist:
            return HttpResponse("Company does not exist.", status=400)

        # User verification
        if not is_employer(request.user):
            return HttpResponse("User must be an employer.", status=400)

        if not is_employer_in_company(request.user, company):
            return HttpResponse("Employer is not involved in this company.", status=400)

        # Input validation
        serializer = EmployerPartialUpdateInputSerializer(data=request.data)
        if not serializer.is_valid():
            return HttpResponse(serializer.errors, status=400)

        validated_data = serializer.validated_data
        processed_data = remap_keys(
            validated_data, self.input_field_to_model_field_mapping
        )

        # Update the employer profile/company
        for model_field, value in processed_data.items():
            setattr(company, model_field, value)
        company.save()

        return HttpResponse("Company successfully updated.", status=200)
