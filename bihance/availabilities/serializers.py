from .models import Timings
from applications.serializers import UserSerializer
from rest_framework import serializers


class AvailabilitySerializer(serializers.ModelSerializer):
    employee = UserSerializer(source='employee_id', read_only=True)

    class Meta:
        model = Timings
        fields = [
           'time_id', 'start_time', 'end_time', 'employee', 'title' 
        ]


