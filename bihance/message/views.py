from .models import Message, MessageFile
from .serializers import (   
    MessageListInputSerializer, MessageSerializer, MessageFileSerializer, 
    MessageCreateInputSerializer, MessagePartialUpdateInputSerializer, MessageDestroyInputSerializer
)
from .utils import get_user_and_application, validate_user_in_application, validate_user_is_sender
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from rest_framework import permissions, viewsets


# Frontend -> UploadThing to manage actual files 
# Backend -> MessageFile db to manage file urls 
class MessageViewSet(viewsets.ModelViewSet): 
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_input_serializer_class(self): 
        match self.action:
            case "list":
                return MessageListInputSerializer
            case "create":
                return MessageCreateInputSerializer
            case "partial_update":
                return MessagePartialUpdateInputSerializer
            case "destroy":
                return MessageDestroyInputSerializer
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
            
        # Different ways to retrive data
        if since: 
            messages = Message.objects.filter(date__gte=since, application_id=application_id)
        else: 
            messages = Message.objects.filter(application_id=application_id)
            
        message_files = MessageFile.objects.filter(message_id__in=messages)

        # Packing serialized data together 
        messages_serializer = MessageSerializer(messages, many=True)
        message_files_serializer = MessageFileSerializer(message_files, many=True)  
        combined_data = {
            "messages": messages_serializer.data,
            "message_files": message_files_serializer.data
        }

        return JsonResponse(combined_data, safe=False)
        

    # POST -> messages/
    def create(self, request):
        # Input validation
        input_serializer_class = self.get_input_serializer_class()
        input_serializer = input_serializer_class(data=request.data)
        if not input_serializer.is_valid(): 
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.validated_data
        content = validated_data.get("content")
        application_id = validated_data["applicationId"]
        reply_to_id = validated_data.get("replyToId")
        file_url = validated_data.get("fileUrl")
        file_name = validated_data.get("fileName")
    
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
            content=content if content else "", 
            application_id=application,
            sender_id=user,
            reply_to_id=reply_to_message if reply_to_id else None 
        )
        message_id = message.message_id

        # Create the message file (if applicable)
        if file_name: 
            message_file = MessageFile.objects.create(
                message_id=message,
                sender_id=user,
                file_url=file_url, 
                file_name=file_name,
                file_type=file_name.split(".")[-1] if "." in file_name else "unknown",
                file_size=0 
            )
            message_file_id = message_file.message_file_id

        if file_name: 
            return HttpResponse(f"Message created successfully with message id: {message_id} | message file id: {message_file_id}.", status=200)
        else: 
            return HttpResponse(f"Message created successfully with message id: {message_id}.", status=200)
         

    # PATCH -> messages/message_id
    def partial_update(self, request, pk=None):
        # Input validation
        input_serializer_class = self.get_input_serializer_class()
        input_data = request.data.copy()
        input_data["messageId"] = pk
        input_serializer = input_serializer_class(data=input_data)
        if not input_serializer.is_valid(): 
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.validated_data
        message_id = validated_data["messageId"]
        new_content = validated_data["newContent"]
        application_id = validated_data["applicationId"]

        # Try to retrieve the message record
        try: 
            message = Message.objects.get(message_id=message_id)
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
        # Input validation
        input_serializer_class = self.get_input_serializer_class()
        input_data = {
            "messageId": pk
        }
        input_serializer = input_serializer_class(data=input_data)
        if not input_serializer.is_valid(): 
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.validated_data
        message_id = validated_data["messageId"]
        
        # Try to retrieve the message record
        try: 
            message = Message.objects.get(message_id=message_id)
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

        # Try to retrieve the message file (if exists)
        message_file = None
        try:
            message_file = MessageFile.objects.get(message_id=message_id)
        except MessageFile.DoesNotExist: 
            pass 
        
        # Perform hard delete of message file
        if message_file:
            message_file.delete()
            return HttpResponse("Message and message file successfully deleted.", status=200)

        return HttpResponse("Message successfully deleted.", status=200)

        
