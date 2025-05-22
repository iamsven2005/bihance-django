from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.decorators import action

from .models import CompanyFollow, EmployerProfile
from .utils import to_json_object


class CompanyViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # GET multiple -> companies/
    def list(self, request):
        all_companies = (
            EmployerProfile.objects.select_related("employer_id")
            .prefetch_related(Prefetch("employer_id__job_set"), "file_set")
            .all()
        )
        result = []

        for company in all_companies:
            company_json = to_json_object(company)
            result.append(company_json)

        return JsonResponse(result, safe=False)

    # GET single -> companies/:company_id
    def retrieve(self, request, pk=None):
        single_company = get_object_or_404(
            EmployerProfile.objects.select_related("employer_id").prefetch_related(
                Prefetch("employer_id__job_set"), "file_set"
            ),
            pk=pk,
        )

        company_json = to_json_object(single_company)
        return JsonResponse(company_json)

    # POST -> companies/:company_id/follow
    @action(detail=True, methods=["post"])
    def follow(self, request, pk=None):
        single_company = get_object_or_404(EmployerProfile, pk=pk)
        follow, created = CompanyFollow.objects.get_or_create(
            follower_id=request.user, company_id=single_company
        )
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
        user_is_following = CompanyFollow.objects.filter(
            follower_id=request.user.id, company_id=pk
        ).exists()
        return HttpResponse(f"isFollowing: {user_is_following}.", status=200)

    # GET -> companies/:company_id/followers
    @action(detail=True, methods=["get"])
    def followers(self, request, pk=None):
        get_object_or_404(EmployerProfile, pk=pk)
        followers_count = CompanyFollow.objects.filter(company_id=pk).count()
        return HttpResponse(f"followersCount: {followers_count}.", status=200)
