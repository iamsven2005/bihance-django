from rest_framework import serializers
from .models import SavedJob

class SavedJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedJob
        fields = ['id', 'job', 'saved_at']
