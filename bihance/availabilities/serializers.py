from rest_framework import serializers
from utils.utils import detect_extra_fields

from .models import Timing


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Timing
        fields = ["time_id", "start_time", "end_time", "employee_id", "title"]
        depth = 0


class AvailabilityCreateInputSerializer(serializers.Serializer):
    startTime = serializers.DateTimeField()
    endTime = serializers.DateTimeField()
    title = serializers.CharField(required=False)

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)

        if data["startTime"] > data["endTime"]:
            raise serializers.ValidationError("Start time cannot exceed end time.")
        return data
