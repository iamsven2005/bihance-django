import uuid

from django.db import models
from django.utils import timezone

from applications.models import Application, User


class Message(models.Model):
    message_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, db_column="messageId"
    )
    content = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    application_id = models.ForeignKey(
        Application, on_delete=models.DO_NOTHING, db_column="applicationId"
    )
    sender_id = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, db_column="senderId"
    )
    is_edited = models.BooleanField(default=False, db_column="isEdited")
    is_deleted = models.BooleanField(default=False, db_column="isDeleted")
    last_edited_at = models.DateTimeField(
        blank=True, null=True, db_column="lastEditedAt"
    )
    reply_to_id = models.ForeignKey(
        "self",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        db_column="replyToId",
    )

    class Meta:
        db_table = "Message"

    def __str__(self):
        return str(self.message_id)
