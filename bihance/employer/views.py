from .serializers import EmployerCreateInputSerializer
from applications.models import User
from companies.models import EmployerProfile
from django.http import HttpResponse
from rest_framework import permissions, viewsets
from utils.utils import check_is_employer


class EmployerViewSet(viewsets.ViewSet):
    queryset = EmployerProfile.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    # POST -> employer/
    def create(self, request): 
        # User verification
        is_employer = check_is_employer(request.user.id)
        if not is_employer: 
            return HttpResponse("User must be an employer.", status=400)
        
        # Retrieve the employer record 
        employer = User.objects.get(id=request.user.id)
        
        # Input validation
        serializer = EmployerCreateInputSerializer(data=request.data)
        if not serializer.is_valid(): 
            return HttpResponse(serializer.errors, status=400)
        
        validated_data = serializer.validated_data
        
        company_name = validated_data["companyName"]
        company_website = validated_data["companyWebsite"]
        contact_name = validated_data.get("contactName")
        contact_role = validated_data.get("contactRole")
        company_size = validated_data.get("companySize")
        industry = validated_data.get("industry")
        talent_needs = validated_data.get("talentNeeds")
        work_style = validated_data.get("workStyle")
        hiring_timeline = validated_data.get("hiringTimeline")
        featured_partner = validated_data.get("featuredPartner")
        image_url = validated_data.get("imageUrl") 
        
        # Check if the employer profile exists already 
        try: 
            # UNIQUE constraint
            EmployerProfile.objects.get(
                employer_id=employer,
                company_name=company_name,
                company_website=company_website
            )
            return HttpResponse("Employer profile exists already.", status=400)
        
        except EmployerProfile.DoesNotExist: 
            pass 

        # Create the new employer profile 
        employer_company = EmployerProfile.objects.create(
            employer_id=employer, 
            company_name=company_name, 
            company_website=company_website,
            contact_name=contact_name if contact_name else None,
            contact_role=contact_role if contact_role else None,
            company_size=company_size if company_size else None,
            industry=industry if industry else None,
            talent_needs=talent_needs if talent_needs else None,
            work_style=work_style if work_style else None,
            hiring_timeline=hiring_timeline if hiring_timeline else None,
            featured_partner=featured_partner if featured_partner else None,
            image_url=image_url if image_url else None
        )
        company_id = employer_company.company_id

        return HttpResponse(f"Employer profile successfully created with company id: {company_id}.", status=200)


    # PATCH -> employer/company_id
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
        serializer = EmployerCreateInputSerializer(data=request.data)
        if not serializer.is_valid(): 
            return HttpResponse(serializer.errors, status=400)
        
        validated_data = serializer.validated_data

        # Update the employer profile record
        data_key_to_model_field_mapping = {
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
            "imageUrl": "image_url",
        }       

        for key, value in validated_data.items(): 
            model_field = data_key_to_model_field_mapping[key]
            setattr(employer_company, model_field, value)
        
        employer_company.save()
        return HttpResponse("Employer profile successfully updated.", status=200)
            

        