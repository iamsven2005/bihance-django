from django.http import HttpResponse
from rest_framework import permissions, viewsets
from utils.utils import (
    check_is_employee,
    get_user_and_application,
    validate_user_in_application,
)

from .serializers import ReviewPartialUpdateInputSerializer


class ReviewsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # PATCH -> reviews/:application_id
    def partial_update(self, request, pk=None):
        # User verification
        user, application = get_user_and_application(
            user_id=request.user.id, application_id=pk
        )
        is_valid = validate_user_in_application(user, application)
        if not is_valid:
            return HttpResponse(
                "This user is not the employer or employee in the application.",
                status=403,
            )

        # Specify user role
        if check_is_employee(user):
            user_role = "employee"
        else:
            user_role = "employer"

        # Input validation
        serializer = ReviewPartialUpdateInputSerializer(data=request.data)
        if not serializer.is_valid():
            return HttpResponse(serializer.errors, status=400)

        validated_data = serializer.data
        content = validated_data["content"]
        rating = validated_data.get("rating")

        if rating:
            combined_review = content + " | Rating:" + rating
        else:
            combined_review = content

        # Update the appropriate field
        if user_role == "employee":
            application.employee_review = combined_review
        else:
            application.employer_review = combined_review

        application.save()
        return HttpResponse(
            f"Application updated successfully with {user_role} review.", status=200
        )
