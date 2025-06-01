from applications.models import User
from applications.serializers import UserSerializer
from django.core.paginator import Paginator
from django.db.models import Q

from .serializers import InterestSerializer, SkillSerializer


def to_json_object(user):
    user_serializer = UserSerializer(user)
    data = {"user": user_serializer.data}

    associated_skills = user.skill_set.all()
    if associated_skills:
        skill_serializer = SkillSerializer(associated_skills, many=True)
        data["skills"] = skill_serializer.data
    else:
        data["skills"] = None

    associated_interests = user.interest_set.all()
    if associated_interests:
        interest_serializer = InterestSerializer(associated_interests, many=True)
        data["interests"] = interest_serializer.data
    else:
        data["interests"] = None

    return data


def search_users_with_paginator(skills=[], name="", page=1, limit=10):
    # Paginate backend model data, for faster (although more fragmented) responses
    try:
        # Build query filters
        filters = Q()

        if name:
            # Extend the current filter with AND
            filters &= Q(first_name__icontains=name) | Q(last_name__icontains=name)

        # Get queryset
        queryset = (
            User.objects.filter(filters)
            .prefetch_related("interest_set", "skill_set")
            .order_by("-created_at")
        )

        if skills:
            # Only keep the users with matching skills
            # Skills is an array of skill name strings
            filtered_users = []
            for user in queryset:
                has_matching_skill = False
                for skill in user.skill_set.all():
                    if skill.name in skills:
                        has_matching_skill = True
                        break

                if has_matching_skill:
                    filtered_users.append(user)

            # Manual pagination, since no longer a queryset :<
            start = (page - 1) * limit
            end = start + limit
            page_users = filtered_users[start:end]
            total_users = len(filtered_users)
            total_pages = (total_users + limit - 1) // limit

        else:
            # Use Django's Paginator
            paginator = Paginator(queryset, limit)
            page_users = paginator.get_page(page)
            total_users = paginator.count
            total_pages = paginator.num_pages

        # Convert page_users to expected format
        users_data = []
        for user in page_users:
            user_json = to_json_object(user)
            users_data.append(user_json)

        return {
            "users": users_data,
            "totalUsers": total_users,
            "totalPages": total_pages,
        }

    except Exception as error:
        raise Exception(f"Error searching users: {error}")
