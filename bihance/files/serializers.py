from .models import Files, AssociatedType
from rest_framework import serializers
from utils.utils import detect_extra_fields


class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = [
           'file_key', 'file_url', 'file_name', 'file_type', 'file_size' 
        ]


class FilesListInputSerializer(serializers.Serializer): 
    associatedType = serializers.ChoiceField(choices=AssociatedType.choices)
    associatedObjectId = serializers.CharField() 

    def validate(self, data): 
        detect_extra_fields(self.initial_data, self.fields)
        return data


class FilesCreateInputSerializer(serializers.Serializer): 
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
    

