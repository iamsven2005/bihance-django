from .models import Message
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
    class Meta:
        model = Message
        fields = [
           'message_id', 'content', 'date', 'application_id', 'sender_id', 
           'is_edited', 'is_deleted', 'last_edited_at', 'reply_to_id'
        ]
        depth = 0
   

class MessageCreateInputSerializer(serializers.Serializer): 
    content = serializers.CharField(default="")
    applicationId = serializers.UUIDField()
    replyToId = serializers.UUIDField(required=False)
    hasFile = serializers.BooleanField()

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)
        if not data['content'] and not data['hasFile']: 
            raise serializers.ValidationError("Text content and file cannot both be missing.")
        
        return data


class MessagePartialUpdateInputSerializer(serializers.Serializer): 
    content = serializers.CharField()
    applicationId = serializers.UUIDField()

    def validate(self, data): 
        detect_extra_fields(self.initial_data, self.fields)
        return data


