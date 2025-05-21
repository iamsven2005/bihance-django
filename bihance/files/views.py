from .models import File
from .serializers import FileSerializer, FileCreateInputSerializer, FileListInputSerializer
from applications.models import User, Job
from companies.models import EmployerProfile
from django.http import JsonResponse, HttpResponse
from message.models import Message
from rest_framework import permissions, viewsets


atype_to_aobject_lookup_map = {
    "Message": (Message, "message_id"),
    "User": (User, "id"),
    "Job": (Job, "job_id"),
    "Company": (EmployerProfile, "company_id"),
}

class FilesViewSet(viewsets.ModelViewSet): 
    permission_classes = [permissions.IsAuthenticated]

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
        if associated_type in atype_to_aobject_lookup_map: 
            aobject_lookup_class, aobject_lookup_field = atype_to_aobject_lookup_map[associated_type]
            
            try: 
                # Directly passing the kv pair won't work 
                # Since the lookup_field is interpreted literally, not dynamically
                aobject_lookup_class.objects.get(**{aobject_lookup_field: associated_object_id})
            except aobject_lookup_class.DoesNotExist: 
                return HttpResponse("No associated object found.", status=400)
            
        # Use the associated type to get associated object 
        # Then, get all files linked to associated object
        match associated_type: 
            case "Message": 
                message = Message.objects.get(message_id=associated_object_id)
                files = File.objects.filter(associated_message=message)
            
        file_serializer = FileSerializer(files, many=True)
        return JsonResponse(file_serializer.data, safe=False)
    

    # POST -> files/ 
    def create(self, request): 
        # Input validation
        input_serializer = FileCreateInputSerializer(data=request.data)
        if not input_serializer.is_valid(): 
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.validated_data
        file_key = validated_data["fileKey"]
        file_url = validated_data["fileUrl"]
        file_name = validated_data["fileName"]
        file_type = validated_data["fileType"]
        file_size = validated_data["fileSize"]
        associated_type = validated_data["associatedType"]
        associated_object_id = validated_data["associatedObjectId"]

        # Try to retrieve the associated object 
        if associated_type in atype_to_aobject_lookup_map: 
            aobject_lookup_class, aobject_lookup_field = atype_to_aobject_lookup_map[associated_type]
            
            try: 
                associated_object = aobject_lookup_class.objects.get(**{aobject_lookup_field: associated_object_id})
            except aobject_lookup_class.DoesNotExist: 
                return HttpResponse("No associated object found.", status=400)
            
        # Create the new file record 
        file = File(
            file_key=file_key, 
            file_url=file_url,
            file_name=file_name, 
            file_type=file_type, 
            file_size=file_size,
            associated_type=associated_type
        )

        match associated_type: 
            case "Message": 
                file.associated_message = associated_object
                file.save()
    
        return HttpResponse(f"File created successfully with file key: {file_key}.", status=200)
    
        
    # DELETE -> files/:file_key
    def destroy(self, request, pk=None):
        # Try to retrieve the file record 
        try: 
            file = File.objects.get(file_key=pk)
            file.delete()
        except File.DoesNotExist: 
            return HttpResponse("File key does not exist.", status=400)

        return HttpResponse("File successfully deleted.", status=200)
    

        