from .models import EmployerProfile, CompanyFollow
from .serializers import EmployerProfileSerializer
from applications.models import Job
from applications.serializers import JobSerializer
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.decorators import action


class CompanyViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # GET multiple -> companies/
    def list(self, request): 
        all_companies = EmployerProfile.objects.all()
        serializer = EmployerProfileSerializer(all_companies, many=True)
        return JsonResponse(serializer.data, safe=False)


    # GET single -> companies/company_id
    def retrieve(self, request, pk=None): 
        single_company = get_object_or_404(EmployerProfile, pk=pk)
        associated_jobs = Job.objects.filter(employer_id=single_company.employer_id.id)
        company_serializer = EmployerProfileSerializer(single_company)
        job_serializer = JobSerializer(associated_jobs, many=True)
        final_data = {
            "company": company_serializer.data, 
            "jobs": job_serializer.data
        }
        return JsonResponse(final_data)


    # POST -> companies/company_id/follow
    @action(detail=True, methods=["post"])
    def follow(self, request, pk=None): 
        get_object_or_404(EmployerProfile, pk=pk)
        follow, created = CompanyFollow.objects.get_or_create(user_id=request.user.id, company_id=pk)
        if created: 
            # Follow
            return HttpResponse(f"Successfully followed company {pk}.", status=200)
        else: 
            # Unfollow
            follow.delete()
            return HttpResponse(f"Successfully unfollowed company {pk}.", status=200)
        

    # GET -> companies/company_id/is_following
    @action(detail=True, methods=["get"])
    def is_following(self, request, pk=None):
        get_object_or_404(EmployerProfile, pk=pk)
        user_is_following = CompanyFollow.objects.filter(user_id=request.user.id, company_id=pk).exists()
        return HttpResponse(f"isFollowing: {user_is_following}.", status=200)


    @action(detail=True, methods=["get"])
    # GET -> companies/company_id/followers
    def followers(self, request, pk=None): 
        get_object_or_404(EmployerProfile, pk=pk)
        followers_count = CompanyFollow.objects.filter(company_id=pk).count()
        return HttpResponse(f"followersCount: {followers_count}.", status=200)


