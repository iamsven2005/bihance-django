from applications.models import Job
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from files.models import File
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from utils.utils import is_employer, remap_keys

from .models import JobRequirement
from .serializers import (
    JobCreateInputSerializer,
    JobFilteredInputSerializer,
    JobPartialUpdateInputSerializer,
)
from .utils import is_employer_in_job, to_json_object


class JobsViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    input_field_to_model_field_mapping = {
        "name": "name",
        "startDate": "start_date",
        "endDate": "end_date",
        "company": "company",
        "payType": "pay_type",
        "salary": "salary",
        "higherSalary": "higher_salary",
        "duration": "duration",
        "jobType": "job_type",
        "startAge": "start_age",
        "endAge": "end_age",
        "gender": "gender",
        "requirements": "requirements",
        "description": "description",
        "locationName": "location_name",
    }

    # GET multiple -> jobs/
    def list(self, request):
        result = []
        jobs = (
            Job.objects.prefetch_related(
                "application_set", "jobrequirement_set", "file_set"
            )
            .all()
            .order_by("-posted_date")
        )

        for job in jobs:
            job_json = to_json_object(job)
            result.append(job_json)

        return JsonResponse(result, safe=False)

    # GET single -> jobs/:job_id
    def retrieve(self, request, pk=None):
        try:
            job = Job.objects.prefetch_related(
                "application_set", "jobrequirement_set"
            ).get(job_id=pk)
        except Job.DoesNotExist:
            return HttpResponse("No job found.", status=400)

        job_json = to_json_object(job)
        return JsonResponse(job_json)

    # POST -> jobs/
    def create(self, request):
        # User verification
        if not is_employer(request.user):
            return HttpResponse("User is not an employer.", status=400)

        # Input validation
        input_serializer = JobCreateInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.data
        processed_data = remap_keys(
            validated_data, self.input_field_to_model_field_mapping
        )

        # Check if job exists already
        try:
            Job.objects.get(
                name=processed_data["name"],
                start_date=processed_data["start_date"],
                employer_id=request.user,
            )
            return HttpResponse("Job already exists", status=400)
        except Job.DoesNotExist:
            pass

        # Create the new job record
        processed_data["posted_date"] = timezone.now()
        processed_data["employer_id"] = request.user
        new_job = Job.objects.create(**processed_data)

        # Create the job requirements, if any
        job_requirements = validated_data.get("jobRequirements")
        if job_requirements:
            for job_requirement in job_requirements:
                JobRequirement.objects.create(name=job_requirement, job_id=new_job)

        return HttpResponse(
            f"Job successfully created with job id: {new_job.job_id}.", status=200
        )

    # PATCH -> jobs/:job_id
    def partial_update(self, request, pk=None):
        # Try to get the job record
        try:
            job = Job.objects.get(job_id=pk)
        except Job.DoesNotExist:
            return HttpResponse("No job found.", status=400)

        # User verification
        if not is_employer(request.user):
            return HttpResponse("User is not an employer.", status=400)

        if not is_employer_in_job(request.user, job):
            return HttpResponse("Employer is not involved in this job.", status=400)

        # Input validation
        input_serializer = JobPartialUpdateInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.data
        processed_data = remap_keys(
            validated_data, self.input_field_to_model_field_mapping
        )

        # Update the job record
        for model_field, value in processed_data.items():
            setattr(job, model_field, value)
        job.save()

        # Update the job requirements, if any
        job_requirements = validated_data.get("jobRequirements")
        if job_requirements:
            # Delete existing, if any
            current_requirements = JobRequirement.objects.filter(job_id=job)
            current_requirements.delete()

            for job_requirement in job_requirements:
                JobRequirement.objects.create(name=job_requirement, job_id=job)

        return HttpResponse("Job successfully updated.", status=200)

    # DELETE -> jobs/:job_id
    def destroy(self, request, pk=None):
        # Try to get the job record
        try:
            job = Job.objects.get(job_id=pk)
        except Job.DoesNotExist:
            return HttpResponse("No job found.", status=400)

        # User verification
        if not is_employer(request.user):
            return HttpResponse("User is not an employer.", status=400)

        if not is_employer_in_job(request.user, job):
            return HttpResponse("Employer is not involved in this job.", status=400)

        # Delete job requirements, if any
        job_requirements = JobRequirement.objects.filter(job_id=job)
        job_requirements.delete()

        # Delete file, if any
        try:
            file = File.objects.get(associated_job=job)
            file.delete()
        except File.DoesNotExist:
            pass

        # Delete job
        job.delete()

        return HttpResponse("Job successfully deleted.", status=200)

    # GET -> jobs/filtered/
    @action(detail=False, methods=["get"])
    def filtered(self, request):
        # Input validation
        input_serializer = JobFilteredInputSerializer(data=request.query_params)
        if not input_serializer.is_valid():
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.data
        job_type = validated_data.get("jobType")
        location = validated_data.get("location")
        search = validated_data.get("search")

        queryset = (
            Job.objects.prefetch_related("application_set", "jobrequirement_set")
            .all()
            .order_by("-posted_date")
        )
        filters = {}

        if job_type:
            filters["job_type"] = job_type
        if location:
            filters["location_name__icontains"] = location

        queryset = queryset.filter(**filters)
        if search:
            # Stage 1 of filtering
            filtered_jobs_1 = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

            # Stage 2 of filtering
            filtered_jobs_2 = []
            for job in queryset:
                has_matching_requirement = False
                for requirement in job.jobrequirement_set.all():
                    if requirement.name == search:
                        has_matching_requirement = True
                        break

                if has_matching_requirement:
                    filtered_jobs_2.append(job)

            # OR the results from both stages together
            queryset = set(list(filtered_jobs_1) + filtered_jobs_2)

        # Return the filtered result
        result = []
        for job in queryset:
            job_json = to_json_object(job)
            result.append(job_json)

        return JsonResponse(result, safe=False)

    # GET -> jobs/employer_jobs/
    @action(detail=False, methods=["get"])
    def employer_jobs(self, request):
        # User verification
        if not is_employer(request.user):
            return HttpResponse("User is not an employer.", status=400)

        result = []
        jobs = (
            Job.objects.prefetch_related("application_set", "jobrequirement_set")
            .filter(employer_id=request.user)
            .order_by("-posted_date")
        )

        for job in jobs:
            job_json = to_json_object(job)
            result.append(job_json)

        return JsonResponse(result, safe=False)
