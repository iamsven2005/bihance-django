from django.http import HttpResponse, JsonResponse
from rest_framework import permissions, viewsets
from utils.utils import is_employee

from .models import Timing
from .serializers import (
    AvailabilityCreateInputSerializer,
    AvailabilitySerializer,
)
from .utils import is_employee_in_timing


class AvailabilitiesViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # GET multiple -> availabilities/
    def list(self, request):
        # User verification
        if not is_employee(request.user):
            return HttpResponse("User must be an employee.", status=400)

        # Retrieve and validate data
        employee_availabilities = Timing.objects.filter(
            employee_id=request.user
        ).order_by("start_time")
        serializer = AvailabilitySerializer(employee_availabilities, many=True)
        return JsonResponse(serializer.data, safe=False)

    # POST -> availabilities/
    def create(self, request):
        # User verification
        if not is_employee(request.user):
            return HttpResponse("User must be an employee.", status=400)

        # Input validation
        input_serializer = AvailabilityCreateInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.validated_data
        start_time = validated_data["startTime"]
        end_time = validated_data["endTime"]
        title = validated_data.get("title")

        # Check if the availability exists already
        try:
            # UNIQUE constraint
            Timing.objects.get(
                employee_id=request.user, start_time=start_time, end_time=end_time
            )
            # No exception raised, availability exists
            return HttpResponse("Availability already exists.", status=400)

        except Timing.DoesNotExist:
            pass

        # Check if the availability start-end time overlaps with existing ones
        current_availabilities = Timing.objects.filter(employee_id=request.user)
        has_overlap = False
        other_start_time = None
        other_end_time = None

        for availability in current_availabilities:
            if availability.start_time > end_time or availability.end_time < start_time:
                continue
            else:
                has_overlap = True
                other_start_time = availability.start_time
                other_end_time = availability.end_time
                break

        if has_overlap:
            return HttpResponse(
                f"New availability from {start_time} to {end_time} overlaps with current availability from {other_start_time} to {other_end_time}.",
                status=400,
            )

        # Create the availability
        new_availability = Timing.objects.create(
            employee_id=request.user,
            start_time=start_time,
            end_time=end_time,
            title=title if title else None,
        )
        new_availability_id = new_availability.time_id

        return HttpResponse(
            f"Availability created successfully with availability_id: {new_availability_id}.",
            status=200,
        )

    # DELETE -> availability/:availability_id
    def destroy(self, request, pk=None):
        # Try to retrieve the timings record
        try:
            timing = Timing.objects.get(time_id=pk)
        except Timing.DoesNotExist:
            return HttpResponse(f"Availability with {pk} not found.", status=404)

        # User verification
        if not is_employee(request.user):
            return HttpResponse("User must be an employee.", status=400)

        if not is_employee_in_timing(request.user, timing):
            return HttpResponse("Employee is not involved in this timing.", status=400)

        # Perform delete
        availability_to_delete = Timing.objects.get(time_id=pk)
        availability_to_delete.delete()
        return HttpResponse("Availability successfully deleted.", status=200)
