from .models import Application, User, Job
from .serializers import (
    ApplicationSerializer,
    ApplicationListInputSerializer,
    ApplicationCreateInputSerializer,
    ApplicationPartialUpdateInputSerializer,
    ApplicationDestroyInputSerializer
)
from .utils import get_employee_applications, get_all_applications, send_email
from django.http import HttpResponse, JsonResponse
from rest_framework import permissions, viewsets
from utils.utils import check_is_employee, check_is_employer


class ApplicationsViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_input_serializer_class(self): 
        match self.action:
            case "list":
                return ApplicationListInputSerializer
            case "create":
                return ApplicationCreateInputSerializer
            case "partial_update":
                return ApplicationPartialUpdateInputSerializer
            case "destroy":
                return ApplicationDestroyInputSerializer
            case _:
                raise ValueError("Failed to get valid input serializer class.")


    # GET multiple -> applications/
    def list(self, request):
        # Input validation
        input_serializer_class = self.get_input_serializer_class()
        input_serializer = input_serializer_class(data=request.query_params)
        if not input_serializer.is_valid(): 
            return HttpResponse(input_serializer.errors, status=400)
            
        serialized_data = input_serializer.validated_data
        application_status = serialized_data.get("applicationStatus")
        user_only = serialized_data.get("userOnly")

        # Different ways to retrieve data    
        if user_only:
            # User should be EMPLOYEE
            is_employee = check_is_employee(request.user.id)
            if not is_employee: 
                return HttpResponse("User must be an employee.", status=400)                
            applications = get_employee_applications(employee_id=request.user.id)

        else:
            # User can be either EMPLOYEE or EMPLOYER
            if application_status is None: 
                applications = get_all_applications(user_id=request.user.id, application_status=None)
            else: 
                applications = get_all_applications(user_id=request.user.id, application_status=int(application_status))

        # Serialize each row/record in the data into a dictionary
        # Return the serialized data! (list of dictionaries)
        serializer = ApplicationSerializer(applications, many=True)
        return JsonResponse(serializer.data, safe=False)


    # POST -> applications/
    def create(self, request):
        # User should be EMPLOYEE
        is_employee = check_is_employee(request.user.id)
        if not is_employee: 
            return HttpResponse("User must be an employee.", status=400)

        # Input validation
        input_serializer_class = self.get_input_serializer_class()
        input_serializer = input_serializer_class(data=request.data)
        if not input_serializer.is_valid(): 
            return HttpResponse(input_serializer.errors, status=400)
        
        serialized_data = input_serializer.validated_data
        job_id = serialized_data["jobId"]
        employer_id = serialized_data["employerId"]
        
        # Try to retrieve the job record 
        try: 
            job_record = Job.objects.get(job_id=job_id)       
        except Job.DoesNotExist:
            return HttpResponse(f"No job corresponding to the application.", status=404)
        
        # Try to retrieve the employee record 
        employee_id = request.user.id
        try: 
            employee_record = User.objects.get(id=employee_id)
        except User.DoesNotExist:
            return HttpResponse(f"No employee corresponding to the application.", status=404)
        
        # Try to retrieve the employer record
        try: 
            employer_record = User.objects.get(id=employer_id)
        except User.DoesNotExist:
            return HttpResponse(f"No employer corresponding to the application.", status=404)
        
        # Check if the applications exists already 
        try:
            # UNIQUE constraint
            Application.objects.get(
                job_id=job_record,
                employee_id=employee_record,
            )  
            # No exception raised, application exists 
            return HttpResponse("Application already exists.", status=400)            
        
        except Application.DoesNotExist: 
            pass

        # Create the application
        new_application = Application.objects.create(
            job_id=job_record,
            accept=1, # 1 means pending
            employee_id=employee_record,
            employer_id=employer_id
        )
        new_application_id = new_application.application_id

        # Send email to EMPLOYEE 
        if employee_record.email: 
            send_email(
                recipient_list=[employee_record.email],
                subject="Job Application Submitted", 
                message=f"You have successfully applied for {job_record.name}."
            )
        
        # Send email to EMPLOYER 
        if employer_record.email:
            send_email(
                recipient_list=[employer_record.email], 
                subject="New Job Application",
                message=f"You have a new job application for {job_id}, from {employee_id}."
            )

        return HttpResponse(f"Application created successfully with application id: {new_application_id}.", status=200) 


    # PATCH -> applications/application_id
    def partial_update(self, request, pk=None): 
        # User should be EMPLOYER
        is_employer = check_is_employer(request.user.id)
        if not is_employer: 
            return HttpResponse("User must be an employer.", status=400)  
        
        # Input validation
        input_serializer_class = self.get_input_serializer_class()
        input_data = {
            "applicationId": pk,
            "newStatus": request.data.get("newStatus")
        }
        input_serializer = input_serializer_class(data=input_data)
        if not input_serializer.is_valid(): 
            return HttpResponse(input_serializer.errors, status=400)
        
        serialized_data = input_serializer.validated_data
        application_id = serialized_data["applicationId"]
        new_status = serialized_data["newStatus"]
        
        # Try to retrieve the application record 
        try: 
            application_to_update = Application.objects.get(application_id=application_id)

            # Quirky Django behaviour 
            # When accessing FK field, doesnt give FK value, gives the entire PK object!
            job_id = application_to_update.job_id.job_id        
            job_name = Job.objects.get(job_id=job_id).name
            employee_id = application_to_update.employee_id.id
            employee_email = User.objects.get(id=employee_id).email

            application_to_update.accept = new_status
            application_to_update.save()

        except Application.DoesNotExist: 
            return HttpResponse(f"Application with {application_id} not found.", status=404)
        
        # Send confirmation email to EMPLOYEE
        if new_status == 2:
            email_message = f"Congratulations, you have been accepted for {job_name}."
        else: 
            email_message = f"Sorry, you have been rejected from {job_name}."

        if employee_email: 
            send_email(
                recipient_list=[employee_email],
                subject="Job Application Outcome",
                message=email_message
            )

        return HttpResponse("Application successfully updated.", status=200)


    # DELETE -> applications/application_id
    def destroy(self, request, pk=None): 
        # User should be EMPLOYEE 
        is_employee = check_is_employee(request.user.id)
        if not is_employee: 
            return HttpResponse("User must be an employee.", status=400)  
        
        # Input validation
        input_serializer_class = self.get_input_serializer_class()
        input_data = {
            "applicationId": pk,
        }
        input_serializer = input_serializer_class(data=input_data)
        if not input_serializer.is_valid(): 
            return HttpResponse(input_serializer.errors, status=400)
        
        serialized_data = input_serializer.validated_data
        application_id = serialized_data["applicationId"]

        # Try to retrieve the application record
        try:
            application_to_delete = Application.objects.get(application_id=application_id)
            job_id = application_to_delete.job_id.job_id
            job_name = Job.objects.get(job_id=job_id).name
            application_to_delete.delete()

        except Application.DoesNotExist:
            return HttpResponse(f'Application with {application_id} not found.', status=404)
        
        # Send confirmation email to EMPLOYEE
        if request.user.email:
            send_email(
                recipient_list=[request.user.email],
                subject="Job Application Withdrawn",
                message=f'You have successfully withdrawn from {job_name}.'
            )
        
        return HttpResponse("Application successfully deleted.", status=200)
        

