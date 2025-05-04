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


class AvailabilityCreateInputSerializer(serializers.Serializer): 
    startTime = serializers.DateTimeField()
    endTime = serializers.DateTimeField()
    title = serializers.CharField(required=False)

    def validate(self, data): 
        if data['startTime'] > data['endTime']: 
            raise serializers.ValidationError("File URL must be provided if file name is given.") 
        return data


class AvailabilityDestroyInputSerializer(serializers.Serializer):
    availabilityId = serializers.UUIDField()


