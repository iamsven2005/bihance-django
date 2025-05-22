from .models import Application, User, Job
from .serializers import (
    ApplicationSerializer,
    JobSerializer,
    UserSerializer,
    ApplicationListInputSerializer,
    ApplicationCreateInputSerializer,
    ApplicationPartialUpdateInputSerializer,
)
from .utils import get_employee_applications, get_all_applications, send_email
from django.http import HttpResponse, JsonResponse
from message.serializers import MessageSerializer
from rest_framework import permissions, viewsets
from utils.utils import check_is_employee, check_is_employer


class ApplicationsViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_input_serializer_class(self): 
        match self.action:
            case "list":
                return ApplicationListInputSerializer
            case "create":
                return ApplicationCreateInputSerializer
            case "partial_update":
                return ApplicationPartialUpdateInputSerializer
            case _:
                raise ValueError("Failed to get valid input serializer class.")


    # GET multiple -> applications/
    def list(self, request):
        # Input validation
        input_serializer_class = self.get_input_serializer_class()
        input_serializer = input_serializer_class(data=request.query_params)
        if not input_serializer.is_valid(): 
            return HttpResponse(input_serializer.errors, status=400)
            
        validated_data = input_serializer.validated_data
        application_status = validated_data.get("applicationStatus")
        user_only = validated_data.get("userOnly")

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

        # Construct the response 
        response = []
        for application in applications: 
            application_serializer = ApplicationSerializer(application)
            job_serializer = JobSerializer(application.job_id)
            employee_serializer = UserSerializer(application.employee_id)

            data = { 
                "application": application_serializer.data,
                "job": job_serializer.data,
                "employee": employee_serializer.data
            }

            if application.message_set.all(): 
                message_serializer = MessageSerializer(application.message_set.all(), many=True)
                data["messages"] = message_serializer.data
            else: 
                data["messages"] = None
            
            response.append(data)

        return JsonResponse(response, safe=False)


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
        
        validated_data = input_serializer.validated_data
        job_id = validated_data["jobId"]
        employer_id = validated_data["employerId"]
        
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
        send_email(
            recipient_list=[employee_record.email],
            subject="Job Application Submitted", 
            message=f"You have successfully applied for {job_record.name}."
        )
        
        # Send email to EMPLOYER 
        send_email(
            recipient_list=[employer_record.email], 
            subject="New Job Application",
            message=f"You have a new job application for {job_id}, from {employee_id}."
        )

        return HttpResponse(f"Application created successfully with application id: {new_application_id}.", status=200) 


    # PATCH -> applications/:application_id
    def partial_update(self, request, pk=None): 
        # Input validation
        input_serializer_class = self.get_input_serializer_class()
        input_serializer = input_serializer_class(data=request.data)
        if not input_serializer.is_valid(): 
            return HttpResponse(input_serializer.errors, status=400)
        
        validated_data = input_serializer.validated_data
        application_status = validated_data.get("applicationStatus")
        bio = validated_data.get("bio")
        
        if application_status:
            assert(bio is None)

            # User should be EMPLOYER
            is_employer = check_is_employer(request.user.id)
            if not is_employer: 
                return HttpResponse("User must be an employer.", status=400)  
            
            # Try to retrieve the application record     
            try: 
                application = Application.objects.get(application_id=pk)

                # Quirky Django behaviour 
                # When accessing FK field, doesnt give FK value, gives the entire PK object!
                job_id = application.job_id.job_id        
                job_name = Job.objects.get(job_id=job_id).name
                employee_id = application.employee_id.id
                employee_email = User.objects.get(id=employee_id).email

                application.accept = application_status
                application.save()

            except Application.DoesNotExist: 
                return HttpResponse(f"Application with {pk} not found.", status=404)
            
            # Send confirmation email to EMPLOYEE
            if application_status == 2:
                email_message = f"Congratulations, you have been accepted for {job_name}."
            if application_status == 3: 
                email_message = f"Sorry, you have been rejected from {job_name}."

            send_email(
                recipient_list=[employee_email],
                subject="Job Application Outcome",
                message=email_message
            )
            return HttpResponse("Application status successfully updated.", status=200)
        
        else: 
            assert(bio is not None)

            # Try to retrieve the application record     
            try: 
                application = Application.objects.get(application_id=pk)
                application.bio = bio
                application.save()

            except Application.DoesNotExist: 
                return HttpResponse(f"Application with {pk} not found.", status=404)
                
            return HttpResponse("Application bio successfully updated.", status=200)


    # DELETE -> applications/:application_id
    def destroy(self, request, pk=None): 
        # User should be EMPLOYEE 
        is_employee = check_is_employee(request.user.id)
        if not is_employee: 
            return HttpResponse("User must be an employee.", status=400)  
        
        # Try to retrieve the application record
        try:
            application_to_delete = Application.objects.get(application_id=pk)
            job_id = application_to_delete.job_id.job_id
            job_name = Job.objects.get(job_id=job_id).name
            application_to_delete.delete()

        except Application.DoesNotExist:
            return HttpResponse(f'Application with {pk} not found.', status=404)
        
        # Send confirmation email to EMPLOYEE
        send_email(
            recipient_list=[request.user.email],
            subject="Job Application Withdrawn",
            message=f'You have successfully withdrawn from {job_name}.'
        )
        
        return HttpResponse("Application successfully deleted.", status=200)
        

