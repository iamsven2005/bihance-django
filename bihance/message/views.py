from .models import Message, MessageFile
from .serializers import MessageSerializer, MessageFileSerializer
from .utils import get_sender_and_application, validate_sender
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import permissions, viewsets


# Frontend -> UploadThing to manage actual files 
# Backend -> MessageFile db to manage file urls 
class MessageViewSet(viewsets.ModelViewSet): 
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    # GET multiple -> messages/
    def list(self, request): 
        try:
            # Data extraction
            since = request.query_params.get("since", None)
            application_id = request.query_params.get("applicationId", None)

            # Data checking 
            if application_id is None:
                return HttpResponse("GET request did not supply application id.", status=500)

            # Sender verification
            # Here, sender is more like who is making the GET request            
            sender, application = get_sender_and_application(sender_id=request.user.id, application_id=application_id)
            validate_sender(sender, application)
            
            # Different ways to retrive data
            if since: 
                since = parse_datetime(since)
                messages = Message.objects.filter(date__gte=since, application_id=application_id)
            else: 
                messages = Message.objects.filter(application_id=application_id)
                
            message_files = MessageFile.objects.filter(message_id__in=messages)

            # Packing serialized data together 
            messages_serializer = MessageSerializer(messages, many=True)
            message_files_serializer = MessageFileSerializer(message_files, many=True)
            combined_data = {
                "message": messages_serializer.data,
                "message_files": message_files_serializer.data
            }
            return JsonResponse(combined_data, safe=False)

        except TypeError:
            return HttpResponse("Failed to serialize messages to JSON. Possible invalid data format.", status=500)
    
        except Exception:
            if since: 
                return HttpResponse(f"GET request for messsages since {since} failed.", status=500)        
            else: 
                return HttpResponse("GET request for all messages failed.", status=500)


    # POST -> messages/
    def create(self, request):
        # Data extraction
        content = request.data.get("content", None)
        application_id = request.data.get("applicationId", None) 
        reply_to_id = request.data.get("replyToId", None)
        file_url = request.data.get("fileUrl", None)
        file_name = request.data.get("fileName", None)

        # Data checking
        if content is None: 
            return HttpResponse("POST request did not supply message content.", status=500)
        if not isinstance(content, str) or content.strip() == "":
            return HttpResponse("POST request came with empty message content.", status=500)
        
        if application_id is None: 
            return HttpResponse("POST request did not supply application id.", status=500)
        
        # Sender verification
        sender, application = get_sender_and_application(sender_id=request.user.id, application_id=application_id)
        is_valid = validate_sender(sender, application)
        if not is_valid: 
            return HttpResponse("This sender is not the employee or employer in the application.", status=403)
        
        # Retrive the reply_to_message (if exists)
        if reply_to_id:
            try:
                reply_to_message = Message.objects.get(message_id=reply_to_id)
            except Message.DoesNotExist: 
                return HttpResponse("No reply-to message corresponding to the message.", status=404)
            
        # Create the message record 
        message = Message.create(
            content=content.strip(), 
            application_id=application,
            sender_id=sender,
            reply_to_id=reply_to_message if reply_to_id else None 
        )
        message_id = message.message_id

        # Create the message file 
        if file_name: 
            message_file = MessageFile.create(
                message_id=message,
                sender_id=sender,
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
        # Data extraction
        message_id = pk
        new_content = request.data.get("newContent", None)
        application_id = request.data.get("applicationId", None) 

        # Data checking
        if new_content is None: 
            return HttpResponse("PATCH request did not supply message content.", status=500)
        if not isinstance(new_content, str) or new_content.strip() == "":
            return HttpResponse("PATCH request came with empty message content.", status=500)
        
        if application_id is None: 
            return HttpResponse("PATCH request did not supply application id.", status=500)
        
        # Sender verification
        # Here, sender is more like who is making the PATCH request          
        sender, application = get_sender_and_application(sender_id=request.user.id, application_id=application_id)
        is_valid = validate_sender(sender, application)
        if not is_valid: 
            return HttpResponse("This sender is not the employee or employer in the application.", status=403)

        # Try to retrieve the message record
        try: 
            message = Message.objects.get(message_id=message_id)
        except Message.DoesNotExist: 
            return HttpResponse("Message to be edited not found.", status=404)

        # Modify the message 
        message.content = new_content.strip()
        message.is_edited = True 
        message.last_edited_at = timezone.now()
        message.save()

        return HttpResponse("Message successfully edited.", status=200)


    # DELETE -> messages/message_id
    def destroy(self, request, pk=None):
        # Data extraction
        message_id = pk
        sender_id = request.user.id

        # Try to retrieve the message record
        try: 
            message = Message.objects.get(message_id=message_id)
        except Message.DoesNotExist: 
            return HttpResponse("Message to be deleted not found.", status=404)
        
        # Sender verification
        # Here, sender is more like who is making the DELETE request
        application_id = message.application_id.application_id
        sender, application = get_sender_and_application(sender_id=sender_id, application_id=application_id)
        is_valid = validate_sender(sender, application)
        if not is_valid: 
            return HttpResponse("This sender is not the employee or employer in the application.", status=403)

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

        
