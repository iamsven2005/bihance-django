from .models import Files
from .serializers import FilesSerializer, FilesCreateInputSerializer, FilesListInputSerializer
from django.http import JsonResponse, HttpResponse
from message.models import Message
from rest_framework import permissions, viewsets


class FilesViewSet(viewsets.ModelViewSet): 
    permission_classes = [permissions.IsAuthenticated]

    # GET multiple -> files/
    def list(self, request): 
        # Input validation
        input_serializer = FilesListInputSerializer(data=request.query_params)
        if not input_serializer.is_valid(): 
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.validated_data
        associated_type = validated_data["associatedType"]
        associated_object_id = validated_data["associatedObjectId"]

        # Try to retrieve the associated object 
        match associated_type: 
            case "Message": 
                try: 
                    Message.objects.get(message_id=associated_object_id)
                except Message.DoesNotExist: 
                    return HttpResponse("No associated object found.", status=400)

        # Use the associated type to get associated object 
        # Then, get all files linked to associated object
        match associated_type: 
            case "Message": 
                message = Message.objects.get(message_id=associated_object_id)
                files = Files.objects.filter(associated_message=message)
            
        file_serializer = FilesSerializer(files, many=True)
        return JsonResponse(file_serializer.data, safe=False)
    

    # POST -> files/ 
    def create(self, request): 
        # Input validation
        input_serializer = FilesCreateInputSerializer(data=request.data)
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
        match associated_type: 
            case "Message": 
                try: 
                    associated_object = Message.objects.get(message_id=associated_object_id)
                except Message.DoesNotExist: 
                    return HttpResponse("No associated object found.", status=400)

        # Create the new file record 
        file = Files(
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
            file = Files.objects.get(file_key=pk)
            file.delete()
        except Files.DoesNotExist: 
            return HttpResponse("File key does not exist.", status=400)

        return HttpResponse("File successfully deleted.", status=200)
    

        