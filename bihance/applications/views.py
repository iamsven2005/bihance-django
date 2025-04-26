from .models import Application, User, Job
from .serializers import ApplicationSerializer
from .utils import get_employee_applications, get_all_applications, send_email
from django.http import JsonResponse, HttpResponse
from rest_framework import permissions, viewsets


class ApplicationsViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    # GET multiple -> applications/
    def list(self, request):
        try:
            # Extract relevant GET parameters 
            # Seems like these are supposed to be optional
            application_status = request.query_params.get("applicationStatus", None) 
            user_only = request.query_params.get("userOnly", None) == "true"
        
            if user_only:
                # User should be EMPLOYEE
                applications = get_employee_applications(employee_id=request.user.id)

            else:
                # User can be either EMPLOYEE or EMPLOYER
                if application_status is None: 
                    applications = get_all_applications(user_id=request.user.id, application_status=None)
                else: 
                    applications = get_all_applications(user_id=request.user.id, application_status=int(application_status))

            # Use serializer to serialize the selected model rows in applications
            # Return the serialized data! (list of dictionaries)
            serializer = ApplicationsViewSet.serializer_class(applications, many=True)
            return JsonResponse(serializer.data, safe=False)
        
        except TypeError:
            return HttpResponse("Failed to serialize applications to JSON. Possible invalid data format.", status=500)
    
        except Exception:
            if user_only: 
                return HttpResponse("GET request for user only applications failed.", status=500)
            
            else: 
                return HttpResponse("GET request for all applications failed.", status=500)

    
    # POST -> applications/
    def create(self, request):
        # User should be EMPLOYEE
        employee_id = request.user.id
        job_id = request.data.get("jobId", None)
        employer_id = request.data.get("employerId", None)

        if job_id is None: 
            return HttpResponse("POST request did not supply job_id to be written.", status=500)
        if employer_id is None: 
            return HttpResponse("POST request did not supply employer_id to be written.", status=500)
        
        # Try to retrieve the job record 
        try: 
            job_record = Job.objects.get(job_id=job_id)       
        except Job.DoesNotExist:
            return HttpResponse(f"No job corresponding to the application.", status=500)
        
        # Try to retrieve the employee record 
        try: 
            employee_record = User.objects.get(id=employee_id)
        except User.DoesNotExist:
            return HttpResponse(f"No employee corresponding to the application.", status=500)
        
        # Try to retrieve the employer record
        try: 
            employer_record = User.objects.get(id=employer_id)
        except User.DoesNotExist:
            return HttpResponse(f"No employer corresponding to the application.", status=500)
        
        # Check if the applications exists already 
        existing_application = Application.objects.filter(
            job_id=job_record,
            employee_id=employee_record,
            employer_id=employer_id
        ).first()

        if existing_application:
            return HttpResponse("Application already exists.", status=400)

        # Create the application
        Application.objects.create(
            job_id=job_record,
            accept=1, # 1 means pending
            employee_id=employee_record,
            employer_id=employer_id
        )

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

        return HttpResponse("Application created successfully.", status=200) 


    # PATCH -> applications/pk
    def partial_update(self, request, pk=None): 
        # User should be EMPLOYER
        application_id = request.data.get("applicationId", None)
        new_status = request.data.get("newStatus", None) 

        if application_id is None: 
            return HttpResponse("PATCH request did not supply application_id to be updated.", status=500)
        if new_status is None: 
            return HttpResponse("PATCH request did not supply new application status.", status=500)
        
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


    # DELETE -> applications/pk
    def destroy(self, request, pk=None): 
        # User should be EMPLOYEE
        application_id = pk 

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
        

