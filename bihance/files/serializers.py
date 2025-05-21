from .models import File, AssociatedType
from rest_framework import serializers
from utils.utils import detect_extra_fields


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [
           'file_key', 'file_url', 'file_name', 'file_type', 'file_size' 
        ]


class FileListInputSerializer(serializers.Serializer): 
    associatedType = serializers.ChoiceField(choices=AssociatedType.choices)
    associatedObjectId = serializers.CharField() 

    def validate(self, data): 
        detect_extra_fields(self.initial_data, self.fields)
        return data


class FileCreateInputSerializer(serializers.Serializer): 
    fileKey = serializers.CharField()
    fileUrl = serializers.URLField()
    fileName = serializers.CharField()
    fileType = serializers.CharField()
    fileSize = serializers.IntegerField()
    associatedType = serializers.ChoiceField(choices=AssociatedType.choices)
    associatedObjectId = serializers.CharField() 

    def validate(self, data): 
        detect_extra_fields(self.initial_data, self.fields)
        return data
    

