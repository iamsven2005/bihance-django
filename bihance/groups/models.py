import uuid

from django.db import models
from django.utils import timezone

from applications.models import Job, User


class RoleType(models.TextChoices):
    ADMIN = "Admin"
    MEMBER = "Member"


class Group(models.Model):
    group_id = models.UUIDField(
        primary_key=True, db_column="groupId", default=uuid.uuid4
    )
    bio = models.TextField()
    creator_id = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, db_column="creatorId"
    )
    # Members are all involved in this job (employee/employer)
    job_id = models.ForeignKey(Job, on_delete=models.DO_NOTHING, db_column="jobId")

    class Meta:
        db_table = "Group"

    def __str__(self):
        return str(self.group_id)


class GroupMember(models.Model):
    member_id = models.UUIDField(
        primary_key=True, db_column="memberId", default=uuid.uuid4
    )
    user_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column="userId")
    group_id = models.ForeignKey(
        Group, on_delete=models.DO_NOTHING, db_column="groupId"
    )
    role = models.TextField(choices=RoleType.choices)

    class Meta:
        db_table = "Group_Member"

    def __str__(self):
        return str(self.member_id)


class GroupMessage(models.Model):
    message_id = models.UUIDField(
        primary_key=True, db_column="messageId", default=uuid.uuid4
    )
    content = models.TextField()
    created_at = models.DateTimeField(db_column="createdAt", default=timezone.now)
    group_id = models.ForeignKey(
        Group, on_delete=models.DO_NOTHING, db_column="groupId"
    )
    sender_id = models.ForeignKey(
        GroupMember, on_delete=models.DO_NOTHING, db_column="senderId"
    )

    is_edited = models.BooleanField(db_column="isEdited", default=False)
    is_deleted = models.BooleanField(db_column="isDeleted", default=False)
    last_edited_at = models.DateTimeField(
        db_column="lastEditedAt", blank=True, null=True
    )
    reply_to_id = models.ForeignKey(
        "self",
        on_delete=models.DO_NOTHING,
        db_column="replyToId",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "Group_Message"

    def __str__(self):
        return str(self.message_id)
