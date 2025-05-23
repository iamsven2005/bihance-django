from applications.models import Application
from applications.serializers import ApplicationSerializer
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from files.models import File
from files.serializers import FileSerializer
from rest_framework import permissions, viewsets
from utils.utils import (
    is_employee,
    is_employee_in_application,
    is_employer,
    is_employer_in_application,
    remap_keys,
)

from .models import Message
from .serializers import (
    MessageCreateInputSerializer,
    MessageListInputSerializer,
    MessagePartialUpdateInputSerializer,
    MessageSerializer,
)
from .utils import is_sender


class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    input_field_to_model_field_mapping = {
        "content": "content",
        "applicationId": "application_id",
        "replyToId": "reply_to_id",
    }

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

        # Try to retrieve the application
        try:
            application = Application.objects.get(application_id=application_id)
        except Application.DoesNotExist:
            return HttpResponse(
                f"Application with {application_id} does not exist.", status=400
            )

        # User verification
        if is_employee(request.user) and not is_employee_in_application(
            request.user, application
        ):
            return HttpResponse(
                "Employee is not involved in this application.", status=400
            )

        if is_employer(request.user) and not is_employer_in_application(
            request.user, application
        ):
            return HttpResponse("Employer is not involved in this application.")

        # Retrive messages
        queryset = (
            Message.objects.prefetch_related("file_set")
            .select_related("application_id", "reply_to_id")
            .order_by("message_id")
        )
        if since:
            messages = queryset.filter(date__gte=since, application_id=application_id)
        else:
            messages = queryset.filter(application_id=application_id)

        # Construct response
        response = []
        for message in messages:
            message_serializer = MessageSerializer(message)
            application_serializer = ApplicationSerializer(message.application_id)

            data = {
                "message": message_serializer.data,
                "application": application_serializer.data,
            }

            if message.reply_to_id:
                reply_to_message_serializer = MessageSerializer(message.reply_to_id)
                data["reply_to_message"] = reply_to_message_serializer.data
            else:
                data["reply_to_message"] = None

            if message.file_set.first():
                file_serializer = FileSerializer(message.file_set.first())
                data["file"] = file_serializer.data
            else:
                data["file"] = None

            response.append(data)

        return JsonResponse(response, safe=False)

    # POST -> messages/
    def create(self, request):
        # Input validation
        input_serializer_class = self.get_input_serializer_class()
        input_serializer = input_serializer_class(data=request.data)
        if not input_serializer.is_valid():
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.validated_data
        processed_data = remap_keys(
            validated_data, self.input_field_to_model_field_mapping
        )

        # Try to retrieve the application
        try:
            application = Application.objects.get(
                application_id=processed_data["application_id"]
            )
        except Application.DoesNotExist:
            return HttpResponse(
                f"Application with {processed_data['application_id']} does not exist.",
                status=400,
            )

        # User verification
        if is_employee(request.user) and not is_employee_in_application(
            request.user, application
        ):
            return HttpResponse(
                "Employee is not involved in this application.", status=400
            )

        if is_employer(request.user) and not is_employer_in_application(
            request.user, application
        ):
            return HttpResponse("Employer is not involved in this application.")

        # Retrive the reply_to_message (if exists)
        if "reply_to_id" in processed_data:
            try:
                reply_to_message = Message.objects.get(
                    message_id=processed_data["reply_to_id"]
                )
                processed_data["reply_to_id"] = reply_to_message
            except Message.DoesNotExist:
                return HttpResponse(
                    "No reply-to message corresponding to the message.", status=404
                )

        # Create the message record
        processed_data["application_id"] = application
        processed_data["sender_id"] = request.user
        message = Message.objects.create(**processed_data)
        message_id = message.message_id

        return HttpResponse(
            f"Message created successfully with message id: {message_id}.", status=200
        )

    # PATCH -> messages/message_id
    def partial_update(self, request, pk=None):
        # Input validation
        input_serializer_class = self.get_input_serializer_class()
        input_serializer = input_serializer_class(data=request.data)
        if not input_serializer.is_valid():
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.validated_data
        processed_data = remap_keys(
            validated_data, self.input_field_to_model_field_mapping
        )

        # Try to retrieve the application
        try:
            application = Application.objects.get(
                application_id=processed_data["application_id"]
            )
        except Application.DoesNotExist:
            return HttpResponse(
                f"Application with {processed_data['application_id']} does not exist.",
                status=400,
            )

        # Try to retrieve the message record
        try:
            message = Message.objects.get(message_id=pk)
        except Message.DoesNotExist:
            return HttpResponse("Message to be edited not found.", status=404)

        # User verification
        if is_employee(request.user) and not is_employee_in_application(
            request.user, application
        ):
            return HttpResponse(
                "Employee is not involved in this application.", status=400
            )

        if is_employer(request.user) and not is_employer_in_application(
            request.user, application
        ):
            return HttpResponse("Employer is not involved in this application.")

        if not is_sender(request.user, message):
            return HttpResponse("User is not the message sender.", status=400)

        # Modify the message
        message.content = processed_data["content"]
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

        # Try to retrieve the application
        try:
            application = Application.objects.get(
                application_id=message.application_id.application_id
            )
        except Application.DoesNotExist:
            return HttpResponse("Application does not exist.", status=400)

        # User verification
        if is_employee(request.user) and not is_employee_in_application(
            request.user, application
        ):
            return HttpResponse(
                "Employee is not involved in this application.", status=400
            )

        if is_employer(request.user) and not is_employer_in_application(
            request.user, application
        ):
            return HttpResponse("Employer is not involved in this application.")

        if not is_sender(request.user, message):
            return HttpResponse("User is not the message sender.", status=400)

        # Perform soft delete of message
        message.content = "[This message has been deleted]"
        message.is_deleted = True
        message.save()

        # Try to retrieve the associated files (if exists)
        associated_files = File.objects.filter(associated_message=message)
        associated_files.delete()

        return HttpResponse("Message successfully deleted.", status=200)
