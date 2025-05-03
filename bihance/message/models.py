import uuid 

from applications.models import Application, User
from django.db import models
from django.utils import timezone


class Message(models.Model):
    message_id = models.TextField(primary_key=True, default=uuid.uuid4, max_length=36, db_column='msgId')  
    content = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    application_id = models.ForeignKey(Application, on_delete=models.DO_NOTHING, db_column='matchId')  
    sender_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='senderId')
    is_edited = models.BooleanField(default=False, db_column='isEdited')  
    is_deleted = models.BooleanField(default=False, db_column='isDeleted') 
    last_edited_at = models.DateTimeField(blank=True, null=True, db_column='lastEditedAt') 
    reply_to_id = models.ForeignKey('self', on_delete=models.DO_NOTHING, blank=True, null=True, db_column='replyToId')  

    class Meta:
        db_table = 'message'
        indexes = [
            models.Index(fields=['application_id']),
            models.Index(fields=['sender_id']),
            models.Index(fields=['reply_to_id']),
        ]


class MessageFile(models.Model):
    message_file_id = models.TextField(primary_key=True, default=uuid.uuid4, max_length=36, db_column="id")
    message_id = models.ForeignKey(Message, models.DO_NOTHING, db_column='messageId')  
    sender_id = models.ForeignKey(User, models.DO_NOTHING, db_column='userId') 
    file_url = models.URLField(db_column='fileUrl')  
    file_name = models.TextField(db_column='fileName')  
    file_type = models.TextField(db_column='fileType')  
    file_size = models.IntegerField(db_column='fileSize')  
    created_at = models.DateTimeField(default=timezone.now, db_column='createdAt')  

    class Meta:
        db_table = 'messageFile'
        indexes = [
            models.Index(fields=['message_id']),
            models.Index(fields=['sender_id']),
        ]


