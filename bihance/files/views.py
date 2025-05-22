from applications.models import Job, User
from companies.models import EmployerProfile
from django.http import HttpResponse, JsonResponse
from message.models import Message
from rest_framework import permissions, viewsets
from utils.utils import remap_keys

from .models import File
from .serializers import (
    FileCreateInputSerializer,
    FileListInputSerializer,
    FileSerializer,
)


class FilesViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    input_field_to_model_field_mapping = {
        "fileKey": "file_key",
        "fileUrl": "file_url",
        "fileName": "file_name",
        "fileType": "file_type",
        "fileSize": "file_size",
        "associatedType": "associated_type",
    }

    atype_to_aobject_lookup_map = {
        "Message": (Message, "message_id"),
        "User": (User, "id"),
        "Job": (Job, "job_id"),
        "Company": (EmployerProfile, "company_id"),
        # "Group Message" [in future]
    }

    atype_to_model_field_map = {
        "Message": "associated_message",
        "User": "associated_user",
        "Job": "associated_job",
        "Company": "associated_company",
        # "Group Message" [in future]
    }

    # GET multiple -> files/
    def list(self, request):
        # Input validation
        input_serializer = FileListInputSerializer(data=request.query_params)
        if not input_serializer.is_valid():
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.validated_data
        associated_type = validated_data["associatedType"]
        associated_object_id = validated_data["associatedObjectId"]

        # Try to retrieve the associated object
        aobject_lookup_class, aobject_lookup_field = self.atype_to_aobject_lookup_map[
            associated_type
        ]
        try:
            # Directly passing the kv pair won't work
            # Since the lookup_field is interpreted literally, not dynamically
            associated_object = aobject_lookup_class.objects.get(
                **{aobject_lookup_field: associated_object_id}
            )
        except aobject_lookup_class.DoesNotExist:
            return HttpResponse("No associated object found.", status=400)

        # Use the associated object to get all files linked to associated object
        filter_field = self.atype_to_model_field_map[associated_type]
        filter_condition = {filter_field: associated_object}
        files = File.objects.filter(**filter_condition)
        file_serializer = FileSerializer(files, many=True)

        return JsonResponse(file_serializer.data, safe=False)

    # POST -> files/
    def create(self, request):
        # Input validation
        input_serializer = FileCreateInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.validated_data
        associated_type = validated_data["associatedType"]
        associated_object_id = validated_data["associatedObjectId"]

        processed_data = remap_keys(
            validated_data, self.input_field_to_model_field_mapping
        )

        # Try to retrieve the associated object
        aobject_lookup_class, aobject_lookup_field = self.atype_to_aobject_lookup_map[
            associated_type
        ]
        try:
            associated_object = aobject_lookup_class.objects.get(
                **{aobject_lookup_field: associated_object_id}
            )
        except aobject_lookup_class.DoesNotExist:
            return HttpResponse("No associated object found.", status=400)

        # Create the new file record
        file = File(**processed_data)
        target_field = self.atype_to_model_field_map[associated_type]
        setattr(file, target_field, associated_object)
        file.save()

        return HttpResponse(
            f"File created successfully with file key: {file.file_key}.", status=200
        )

    # DELETE -> files/:file_key
    def destroy(self, request, pk=None):
        # Try to retrieve the file record
        try:
            file = File.objects.get(file_key=pk)
            file.delete()
        except File.DoesNotExist:
            return HttpResponse("File key does not exist.", status=400)

        return HttpResponse("File successfully deleted.", status=200)
