from rest_framework import serializers
from utils.utils import detect_extra_fields


class ReviewPartialUpdateInputSerializer(serializers.Serializer): 
    content = serializers.CharField()
    rating = serializers.CharField(required=False)

    def validate_rating(self, value): 
        num_value = int(value)
        if num_value > 5 or num_value < 1: 
            raise serializers.ValidationError("Rating must be from 1 - 5.")

    def validate(self, data): 
        detect_extra_fields(self.initial_data, self.fields)
        return data


