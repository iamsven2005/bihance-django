from .models import EmployerProfile, CompanyFollow
from .serializers import EmployerProfileSerializer
from applications.models import Job
from applications.serializers import JobSerializer
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from files.models import File
from files.serializers import FileSerializer
from rest_framework import permissions, viewsets
from rest_framework.decorators import action


class CompanyViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # GET multiple -> companies/
    def list(self, request): 
        all_companies = EmployerProfile.objects.all()
        result = []

        for company in all_companies: 
            associated_jobs = Job.objects.filter(employer_id=company.employer_id.id)

            try: 
                associated_file = File.objects.get(associated_company=company)
            except File.DoesNotExist: 
                associated_file = None

            company_serializer = EmployerProfileSerializer(company)
            job_serializer = JobSerializer(associated_jobs, many=True)

            final_data = { 
                "company": company_serializer.data, 
                "jobs": job_serializer.data,
            }

            if associated_file is None: 
                result.append(final_data)
            else: 
                file_serializer = FileSerializer(associated_file)
                final_data["file"] = file_serializer.data
                result.append(final_data)
    
        return JsonResponse(result, safe=False)


    # GET single -> companies/:company_id
    def retrieve(self, request, pk=None): 
        single_company = get_object_or_404(EmployerProfile, pk=pk)
        associated_jobs = Job.objects.filter(employer_id=single_company.employer_id.id)
        
        try: 
            associated_file = File.objects.get(associated_company=single_company)
        except File.DoesNotExist: 
            associated_file = None

        company_serializer = EmployerProfileSerializer(single_company)
        job_serializer = JobSerializer(associated_jobs, many=True)

        final_data = {
            "company": company_serializer.data, 
            "jobs": job_serializer.data,
        }

        if associated_file is None: 
            return JsonResponse(final_data)
        else: 
            file_serializer = FileSerializer(associated_file)
            final_data["file"] = file_serializer.data
            return JsonResponse(final_data)


    # POST -> companies/:company_id/follow
    @action(detail=True, methods=["post"])
    def follow(self, request, pk=None): 
        single_company = get_object_or_404(EmployerProfile, pk=pk)
        follow, created = CompanyFollow.objects.get_or_create(follower_id=request.user, company_id=single_company)
        if created: 
            # Follow
            return HttpResponse(f"Successfully followed company {pk}.", status=200)
        else: 
            # Unfollow
            follow.delete()
            return HttpResponse(f"Successfully unfollowed company {pk}.", status=200)
        

    # GET -> companies/:company_id/is_following
    @action(detail=True, methods=["get"])
    def is_following(self, request, pk=None):
        get_object_or_404(EmployerProfile, pk=pk)
        user_is_following = CompanyFollow.objects.filter(follower_id=request.user.id, company_id=pk).exists()
        return HttpResponse(f"isFollowing: {user_is_following}.", status=200)


    # GET -> companies/:company_id/followers
    @action(detail=True, methods=["get"])
    def followers(self, request, pk=None): 
        get_object_or_404(EmployerProfile, pk=pk)
        followers_count = CompanyFollow.objects.filter(company_id=pk).count()
        return HttpResponse(f"followersCount: {followers_count}.", status=200)


