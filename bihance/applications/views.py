from django.views import View
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Application, User, Job
from .utils import get_user_applications, get_all_applications, send_email


class ApplicationsView(LoginRequiredMixin, View):
    def get(self, request): 
        try:
            # Extract relevant GET parameters 
            # Seems like these are supposed to be optional
            application_status = request.GET.get("status", None) 
            user_only = request.GET.get("userOnly", None) == "true"

            if user_only:
                # User should be EMPLOYEE
                applications = get_user_applications(employee_id=request.user.id)

            else:
                # User can be EITHER
                if application_status is None: 
                    applications = get_all_applications(user_id=request.user.id, application_status=None)
                else: 
                    applications = get_all_applications(user_id=request.user.id, application_status=int(application_status))

            # Returns a querySet, hence safe=False
            # Okay for querySet to be empty 
            return JsonResponse(applications, safe=False)
        
        except Exception:
            if user_only: 
                return HttpResponse("GET request for user only applications failed.", status=500)
            
            else: 
                return HttpResponse("GET request for all applications failed.", status=500)


    def post(self, request): 
        # User should be EMPLOYEE
        employee_id = request.user.id
        job_id = request.POST.get("jobId", None)
        employer_id = request.POST.get("employerId", None)

        if job_id is None: 
            return HttpResponse("POST request did not supply job_id to be written.", status=500)
        if employer_id is None: 
            return HttpResponse("POST request did not supply employer_id to be written.", status=500)
        
        # Try to retrieve the job record 
        try: 
            job_record = Job.objects.get(job_id=employer_id)       
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
        
        # Create the application
        Application.objects.create(
            job=job_record,
            # 1 means pending
            accept=1,
            user=employee_record,
            employer_id=employer_id
        )

        # Send email to EMPLOYEE 
        if employee_record.email: 
            send_email(
                to=[employee_record.email],
                subject="Job Application Submitted", 
                message=f"You have successfully applied for {job_record.name}."
            )
        
        # Send email to EMPLOYER 
        if employer_record.email:
            send_email(
                to=[employer_record.email], 
                subject="New Job Application",
                message=f"You have a new job application for {job_id}, from {employee_id}."
            )

        return HttpResponse("Application created successfully.", status=200)


    def patch(self, request): 
        # User should be EMPLOYER
        employer_id = request.user.id
        job_id = request.PATCH.get("jobId", None)
        new_status = request.PATCH.get("status", None) 

        if job_id is None: 
            return HttpResponse("PATCH request did not supply job_id to be updated.", status=500)
        if new_status is None: 
            return HttpResponse("PATCH request did not supply new application status.", status=500)
        
        # Try to retrieve the application record 
        try: 
            application_to_update = Application.objects.get(user=employer_id, job=job_id)
            job_name = application_to_update.job.name
            employee_email = application_to_update.user.email
            application_to_update.accept = new_status
            application_to_update.save()

        except Application.DoesNotExist: 
            return HttpResponse(f"Application with {job_id} not found.", status=404)
        
        # Send confirmation email to EMPLOYEE
        if new_status == 2:
            email_message = f"Congratulations, you have been accepted for {job_name}."
        else: 
            email_message = f"Sorry, you have been rejected from {job_name}."

        if employee_email: 
            send_email(
                to=[employee_email],
                subject="Job Application Outcome",
                message=email_message
            )

        return HttpResponse("Application successfully updated.", status=200)
        

    def delete(self, request): 
        # User should be EMPLOYEE
        employee_id = request.user.id
        job_id = request.GET.get("jobId", None) 

        if job_id is None: 
            return HttpResponse("DELETE request did not supply job_id to be deleted.", status=500)
        
        # Try to retrieve the application record
        try:
            application_to_delete = Application.objects.get(user=employee_id, job=job_id)
            job_name = application_to_delete.job.name
            application_to_delete.delete()

        except Application.DoesNotExist:
            return HttpResponse(f"Application with {job_id} not found.", status=404)
        
        # Send confirmation email to EMPLOYEE
        if request.user.email:
            send_email(
                to=[request.user.email],
                subject="Job Application Withdrawn",
                message=f"You have successfully withdrawn from {job_name}."
            )
        
        return HttpResponse("Application successfully deleted.", status=200)
        

