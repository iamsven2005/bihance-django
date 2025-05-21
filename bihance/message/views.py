from .models import Message
from .serializers import (   
    MessageListInputSerializer, MessageSerializer,
    MessageCreateInputSerializer, MessagePartialUpdateInputSerializer
)
from .utils import validate_user_is_sender
from utils.utils import get_user_and_application, validate_user_in_application
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from rest_framework import permissions, viewsets
from files.models import File
from files.serializers import FileSerializer


class MessageViewSet(viewsets.ModelViewSet): 
    permission_classes = [permissions.IsAuthenticated]

    def get_input_serializer_class(self): 
        match self.action:
            case "list":
                return MessageListInputSerializer
            case "create":
                return MessageCreateInputSerializer
            case "partial_update":
                return MessagePartialUpdateInputSerializer
            case _:
                raise ValueError("Failed to get valid input serializer class.")


    # GET multiple -> messages/
    def list(self, request): 
        # Input validation
        input_serializer_class = self.get_input_serializer_class()
        input_serializer = input_serializer_class(data=request.query_params)
        if not input_serializer.is_valid(): 
            return HttpResponse(input_serializer.errors, status=400)
            
        validated_data = input_serializer.validated_data
        application_id = validated_data["applicationId"]
        since = validated_data.get("since")

        # User verification
        user, application = get_user_and_application(user_id=request.user.id, application_id=application_id)
        is_valid = validate_user_in_application(user, application)
        if not is_valid: 
            return HttpResponse("This user is not the employee or employer in the application.", status=403)
            
        # Retrive messages
        if since: 
            messages = Message.objects.filter(date__gte=since, application_id=application_id).order_by("message_id")
        else: 
            messages = Message.objects.filter(application_id=application_id).order_by("message_id")

        # Retrieve associated files and construct response 
        response = []
        for message in messages: 
            associated_files = File.objects.filter(associated_message=message)
            message_serializer = MessageSerializer(message)

            if not associated_files: 
                response.append({
                    "message": message_serializer.data
                })
            else: 
                files_serializer = FileSerializer(associated_files, many=True)
                response.append({
                    "message": message_serializer.data,
                    "files": files_serializer.data
                })
        
        return JsonResponse(response, safe=False)

        
    # POST -> messages/
    def create(self, request):
        # Input validation
        input_serializer_class = self.get_input_serializer_class()
        input_serializer = input_serializer_class(data=request.data)
        if not input_serializer.is_valid(): 
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.validated_data

        # Content is optional, but defaults to an empty string
        content = validated_data["content"]
        application_id = validated_data["applicationId"]
        reply_to_id = validated_data.get("replyToId")

        # User verification
        user, application = get_user_and_application(user_id=request.user.id, application_id=application_id)
        is_valid = validate_user_in_application(user, application)
        if not is_valid: 
            return HttpResponse("This user is not the employee or employer in the application.", status=403)
        
        # Retrive the reply_to_message (if exists)
        if reply_to_id:
            try:
                reply_to_message = Message.objects.get(message_id=reply_to_id)
            except Message.DoesNotExist: 
                return HttpResponse("No reply-to message corresponding to the message.", status=404)
            
        # Create the message record 
        message = Message.objects.create(
            content=content, 
            application_id=application,
            sender_id=user,
            reply_to_id=reply_to_message if reply_to_id else None 
        )
        message_id = message.message_id

        return HttpResponse(f"Message created successfully with message id: {message_id}.", status=200)
         

    # PATCH -> messages/message_id
    def partial_update(self, request, pk=None):
        # Input validation
        input_serializer_class = self.get_input_serializer_class()
        input_serializer = input_serializer_class(data=request.data)
        if not input_serializer.is_valid(): 
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.validated_data
        new_content = validated_data["newContent"]
        application_id = validated_data["applicationId"]

        # Try to retrieve the message record
        try: 
            message = Message.objects.get(message_id=pk)
        except Message.DoesNotExist: 
            return HttpResponse("Message to be edited not found.", status=404)
        
        # User verification
        user, application = get_user_and_application(user_id=request.user.id, application_id=application_id)
        is_valid = validate_user_in_application(user, application) and validate_user_is_sender(user, message)
        if not is_valid: 
            return HttpResponse("This user is not the owner of the message.", status=403)

        # Modify the message 
        message.content = new_content.strip()
        message.is_edited = True 
        message.last_edited_at = timezone.now()
        message.save()

        return HttpResponse("Message successfully edited.", status=200)


    # DELETE -> messages/message_id
    def destroy(self, request, pk=None):
        # Try to retrieve the message record
        try: 
            message = Message.objects.get(message_id=pk)
        except Message.DoesNotExist: 
            return HttpResponse("Message to be deleted not found.", status=404)
        
        # User verification
        user_id = request.user.id
        application_id = message.application_id.application_id
        user, application = get_user_and_application(user_id=user_id, application_id=application_id)
        is_valid = validate_user_in_application(user, application) and validate_user_is_sender(user, message)
        if not is_valid: 
            return HttpResponse("This user is not owner of the message.", status=403)

        # Perform soft delete of message 
        message.content = "[This message has been deleted]"
        message.is_deleted = True 
        message.save()

        # Try to retrieve the associated files (if exists)
        associated_files = File.objects.filter(associated_message=message)
        associated_files.delete()
        
        return HttpResponse("Message successfully deleted.", status=200)

        
