from applications.models import User
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from utils.utils import remap_keys

from .models import Interest, Skill
from .serializers import UserPartialUpdateInputSerializer, UserSearchInputSerializer
from .utils import search_users_with_paginator, to_json_object


class UsersViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    input_field_to_model_field_mapping = {
        "firstName": "first_name",
        "lastName": "last_name",
        "email": "email",
        "phone": "phone",
        "bio": "bio",
        "age": "age",
    }

    # GET single -> users/:user_id
    def retrieve(self, request, pk=None):
        # Try to retrieve the user
        try:
            user = User.objects.prefetch_related("interest_set", "skill_set").get(id=pk)
        except User.DoesNotExist:
            return HttpResponse("User does not exist.", 400)

        # Construct JSON response
        user_json = to_json_object(user)
        return JsonResponse(user_json)

    # PATCH -> users/:user_id
    def partial_update(self, request, pk=None):
        # Try to retrieve the user
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return HttpResponse("User does not exist.", 400)

        # Input validation
        input_serializer = UserPartialUpdateInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.validated_data

        # Perform updates
        if validated_data.get("toggleRole"):
            # Should not have other fields
            assert len(validated_data) == 1

            if user.employee is None:
                user.employee = True
            else:
                user.employee = not user.employee

            user.save()
            return HttpResponse("Successfully toggled user role.", status=200)

        else:
            # Should not have no values, ie: should be truthy
            assert validated_data

            interests = validated_data.get("interests")
            skills = validated_data.get("skills")

            # Replace existing interests
            if interests:
                associated_interests = Interest.objects.filter(user_id=user)
                associated_interests.delete()
                for interest in interests:
                    Interest.objects.create(
                        user_id=user,
                        name=interest["name"],
                        description=interest["description"],
                    )

            # Replace existing skills
            if skills:
                associated_skills = Skill.objects.filter(user_id=user)
                associated_skills.delete()
                for skill in skills:
                    Skill.objects.create(user_id=user, name=skill["name"])

            # Update user details
            processed_data = remap_keys(
                validated_data, self.input_field_to_model_field_mapping
            )
            for model_field, data in processed_data.items():
                setattr(user, model_field, data)
            user.save()
            return HttpResponse("Successfully updated user details.", status=200)

    # GET multiple -> users/search
    @action(detail=False, methods=["get"])
    def search(self, request):
        # Input validation
        input_serializer = UserSearchInputSerializer(data=request.query_params)
        if not input_serializer.is_valid():
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.validated_data
        skills = validated_data.get("skills")
        name = validated_data.get("name")
        page = validated_data.get("page")
        limit = validated_data.get("limit")

        # Perform user search
        try:
            result = search_users_with_paginator(skills, name, page, limit)
            return JsonResponse(result)
        except Exception as e:
            return HttpResponse(f"Error searching for users: {e}", status=400)

    # GET multiple -> users/skills
    @action(detail=False, methods=["get"])
    def skills(self, request):
        # GROUP BY name
        # Each group is annotated with count
        # This count is derived by applying the Count function to each name group
        # LIMIT to 20
        skill_groups = (
            Skill.objects.values("name")
            .annotate(count=Count("name"))
            .order_by("-count")[:20]
        )

        # list(skill_group) of the form:
        # [{'name': 'React', 'count': 3}, ...]
        return JsonResponse(list(skill_groups), safe=False)
