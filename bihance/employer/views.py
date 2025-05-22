from .serializers import EmployerCreateInputSerializer, EmployerPartialUpdateInputSerializer
from applications.models import User
from companies.models import EmployerProfile
from django.http import HttpResponse
from rest_framework import permissions, viewsets
from utils.utils import check_is_employer, remap_keys


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
        "featuredPartner": "featured_partner"
    }

    # POST -> employer/
    def create(self, request): 
        # User verification
        is_employer = check_is_employer(request.user.id)
        if not is_employer: 
            return HttpResponse("User must be an employer.", status=400)
        
        # Input validation
        serializer = EmployerCreateInputSerializer(data=request.data)
        if not serializer.is_valid(): 
            return HttpResponse(serializer.errors, status=400)
        
        validated_data = serializer.validated_data
        processed_data = remap_keys(validated_data, self.input_field_to_model_field_mapping)

        # Retrieve the employer record 
        employer = User.objects.get(id=request.user.id)
        
        # Check if the employer profile exists already 
        try: 
            # UNIQUE constraint
            EmployerProfile.objects.get(
                employer_id=employer,
                company_name=processed_data["company_name"],
                company_website=processed_data["company_website"]
            )
            return HttpResponse("Employer profile exists already.", status=400)
        
        except EmployerProfile.DoesNotExist: 
            pass 

        # Create the new employer profile 
        processed_data["employer_id"] = employer
        employer_company = EmployerProfile.objects.create(**processed_data)
        company_id = employer_company.company_id

        return HttpResponse(f"Employer profile successfully created with company id: {company_id}.", status=200)


    # PATCH -> employer/:company_id
    def partial_update(self, request, pk=None): 
        # User verification
        is_employer = check_is_employer(request.user.id)
        if not is_employer: 
            return HttpResponse("User must be an employer.", status=400)
        
        # Try to retrieve the employer profile record 
        try: 
            employer_company = EmployerProfile.objects.get(company_id=pk)
        except EmployerProfile.DoesNotExist:
            return HttpResponse("Employer profile does not exist.", status=400)
        
        # Input validation
        serializer = EmployerPartialUpdateInputSerializer(data=request.data)
        if not serializer.is_valid(): 
            return HttpResponse(serializer.errors, status=400)
        
        validated_data = serializer.validated_data
        processed_data = remap_keys(validated_data, self.input_field_to_model_field_mapping)

        # Update the employer profile 
        for model_field, value in processed_data.items(): 
            setattr(employer_company, model_field, value)        
        employer_company.save()

        return HttpResponse("Employer profile successfully updated.", status=200)
            

        