from .models import Timings
from .serializers import AvailabilitySerializer
from applications.models import User
from django.http import JsonResponse, HttpResponse
from django.utils.dateparse import parse_datetime
from rest_framework import permissions, viewsets


class AvailabilitiesViewSet(viewsets.ModelViewSet): 
    queryset = Timings.objects.all()
    serializer_class = AvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    # GET multiple -> availabilities/
    def list(self, request): 
        try:
            # Data extraction
            employee_id = request.user.id

            # Try to retrieve the employee record 
            try: 
                employee_record = User.objects.get(id=employee_id)
            except User.DoesNotExist: 
                return HttpResponse("No employee corresponding to the availability.", status=404)
            
            # Retrieve and serialize data
            employee_availabilites = Timings.objects.filter(employee_id=employee_record).order_by("start_time")
            serializer = AvailabilitiesViewSet.serializer_class(employee_availabilites, many=True)
            return JsonResponse(serializer.data, safe=False)

        except TypeError: 
            return HttpResponse("Failed to serialize availabilities to JSON. Possible invalid data format.", status=500)
        
        except Exception: 
            return HttpResponse("GET request for all availabilities failed.", status=500)
        

    # POST -> availabilities/
    def create(self, request):
        # Data extraction
        employee_id = request.user.id
        start_time = request.data.get("startTime", None)
        end_time = request.data.get("endTime", None)
        title = request.data.get("title", None)

        # Data verification
        if start_time is None: 
            return HttpResponse("POST request did not supply start_time to be written.", status=500)
        if end_time is None: 
            return HttpResponse("POST request did not supply end_time to be written.", status=500)

        start_time = parse_datetime(start_time)
        end_time = parse_datetime(end_time)
        
        # Try to retrieve the employee record 
        try: 
            employee_record = User.objects.get(id=employee_id)
        except User.DoesNotExist: 
            return HttpResponse("No employee corresponding to the availability.", status=404)

        # Check if the availability exists already 
        try: 
            # UNIQUE constraint
            Timings.objects.get(
                employee_id=employee_record,
                start_time=start_time, 
                end_time=end_time
            )
            # No exception raised, availability exists 
            return HttpResponse("Availability already exists.", status=500)     
        
        except Timings.DoesNotExist:  
            pass

        # Check if the end time comes before the start time 
        if end_time < start_time:
            return HttpResponse(f"End time {end_time} cannot come before start time {start_time}", status=500)
        
        # Check if the availability start-end time overlaps with existing ones
        current_availabilities = Timings.objects.filter(employee_id=employee_record)
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
            return HttpResponse(f"New availability from {start_time} to {end_time} overlaps with current availability from {other_start_time} to {other_end_time}", status=500)    

        # Create the availability 
        new_availability = Timings.objects.create(
            employee_id=employee_record,
            start_time=start_time, 
            end_time=end_time,
            title=title if title else None 
        )
        new_availability_id = new_availability.time_id

        return HttpResponse(f"Availability created successfully with availability_id: {new_availability_id}.", status=200) 


    # DELETE -> availability/availability_id
    def destroy(self, request, pk=None): 
        # Data extraction
        availability_id = pk

         # Try to retrieve the timings record
        try:
            availability_to_delete = Timings.objects.get(time_id=availability_id)
            availability_to_delete.delete()
            return HttpResponse("Availability successfully deleted.", status=200)

        except Timings.DoesNotExist:
            return HttpResponse(f'Availability with {availability_id} not found.', status=404)
        

