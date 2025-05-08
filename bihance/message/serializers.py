from .models import Message, MessageFile
from applications.serializers import ApplicationSerializer, UserSerializer
from django.utils import timezone
from rest_framework import serializers
from utils.utils import detect_extra_fields


# Takes a normal dictionary object 
class MessageListInputSerializer(serializers.Serializer): 
    # OK if field values are originally strings 
    # DRF automatically parses 
    applicationId = serializers.UUIDField()
    since = serializers.DateTimeField(required=False)

    def validate_since(self, value): 
        if value > timezone.now():
            raise serializers.ValidationError("The 'since' parameter cannot be in the future.")
        return value
    
    def validate(self, data): 
        detect_extra_fields(self.initial_data, self.fields)
        return data

    
# Takes a model object 
class MessageSerializer(serializers.ModelSerializer):
    application = ApplicationSerializer(source="application_id", read_only=True)
    sender = UserSerializer(source="sender_id", read_only=True)
    reply_to_message = serializers.SerializerMethodField()

    def get_reply_to_message(self, obj):
        # obj -> model object being serialized
        if obj.reply_to_id:
            return MessageSerializer(obj.reply_to_id, context=self.context).data
        return None

    class Meta:
        model = Message
        fields = [
           'message_id', 'content', 'date', 'application', 'sender', 
           'is_edited', 'is_deleted', 'last_edited_at', 'reply_to_message'
        ]
   

class MessageFileSerializer(serializers.ModelSerializer): 
    message = MessageSerializer(source="message_id", read_only=True) 
    sender = UserSerializer(source="sender_id", read_only=True)

    class Meta:
        model = MessageFile
        fields = [
            'message_file_id', 'message', 'sender', 'file_url',
            'file_name', 'file_type', 'file_size', 'created_at'
        ]


class MessageCreateInputSerializer(serializers.Serializer): 
    content = serializers.CharField(required=False)
    applicationId = serializers.UUIDField()
    replyToId = serializers.UUIDField(required=False)
    fileUrl = serializers.URLField(required=False)
    fileName = serializers.CharField(required=False)

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)
        content = data.get("content")
        file_url = data.get("fileUrl")
        file_name = data.get("fileName")

        if not content and not file_url: 
            raise serializers.ValidationError("Either text or file must be included in the message.")
        if file_name and not file_url:
            raise serializers.ValidationError("File URL must be provided if file name is given.")        
        if file_url and not file_name: 
            raise serializers.ValidationError("File name must be provided if file URL is given.")        
        return data


class MessagePartialUpdateInputSerializer(serializers.Serializer): 
    messageId = serializers.UUIDField()
    newContent = serializers.CharField()
    applicationId = serializers.UUIDField()

    def validate(self, data): 
        detect_extra_fields(self.initial_data, self.fields)
        return data


class MessageDestroyInputSerializer(serializers.Serializer):
    messageId = serializers.UUIDField() 

    def validate(self, data): 
        detect_extra_fields(self.initial_data, self.fields)
        return data


