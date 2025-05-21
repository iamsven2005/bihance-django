from .models import Timing
from applications.serializers import UserSerializer
from rest_framework import serializers
from utils.utils import detect_extra_fields


class AvailabilitySerializer(serializers.ModelSerializer):
    employee = UserSerializer(source='employee_id', read_only=True)

    class Meta:
        model = Timing
        fields = [
           'time_id', 'start_time', 'end_time', 'employee', 'title' 
        ]


class AvailabilityCreateInputSerializer(serializers.Serializer): 
    startTime = serializers.DateTimeField()
    endTime = serializers.DateTimeField()
    title = serializers.CharField(required=False)

    def validate(self, data): 
        detect_extra_fields(self.initial_data, self.fields)
        
        if data['startTime'] > data['endTime']: 
            raise serializers.ValidationError("Start time cannot exceed end time.") 
        return data


