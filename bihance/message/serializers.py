from .models import Message, MessageFile
from applications.serializers import ApplicationSerializer, UserSerializer
from rest_framework import serializers


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


