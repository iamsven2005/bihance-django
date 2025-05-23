from applications.models import Application
from django.http import HttpResponse
from rest_framework import permissions, viewsets
from utils.utils import (
    is_employee,
    is_employee_in_application,
    is_employer,
    is_employer_in_application,
)

from .serializers import ReviewPartialUpdateInputSerializer


class ReviewsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # PATCH -> reviews/:application_id
    def partial_update(self, request, pk=None):
        # Try to retrieve the application record
        try:
            application = Application.objects.get(application_id=pk)
        except Application.DoesNotExist:
            return HttpResponse(f"Application with {pk} not found.", status=400)

        # User verification
        if is_employee(request.user):
            if is_employee_in_application(request.user, application):
                user_role = "employee"
            else:
                return HttpResponse("Employee is not involved in the application.")

        if is_employer(request.user):
            if is_employer_in_application(request.user, application):
                user_role = "employer"
            else:
                return HttpResponse("Employer is not involved in the application.")

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
