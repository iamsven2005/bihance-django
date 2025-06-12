from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from applications.models import Job
from utils.utils import detect_extra_fields

from .models import Group, GroupMember, GroupMessage
from .utils import check_new_ids, validate_no_duplicates


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["group_id", "bio", "creator_id", "job_id"]
        depth = 0


class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = ["member_id", "user_id", "group_id", "role"]
        depth = 0


class GroupMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMessage
        fields = [
            "message_id",
            "content",
            "created_at",
            "group_id",
            "sender_id",
            "is_edited",
            "is_deleted",
            "last_edited_at",
            "reply_to_id",
        ]
        depth = 0


class GroupCreateInputSerializer(serializers.Serializer):
    bio = serializers.CharField()
    jobId = serializers.UUIDField()

    # List of user_id strings for the members
    userIds = serializers.ListField(allow_empty=False, child=serializers.UUIDField())

    def validate_jobId(self, value):
        try:
            Job.objects.get(job_id=value)
            return value
        except Job.DoesNotExist:
            raise serializers.ValidationError("Provided Job ID does not exist.")

    def validate_userIds(self, value):
        return validate_no_duplicates(value, "userIds")

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)

        associated_job = Job.objects.get(job_id=data["jobId"])
        user_ids = data["userIds"]
        try:
            check_new_ids(user_ids, associated_job)
        except Exception as e:
            raise serializers.ValidationError(f"Error validating userIds: {e}.")
        return data


class GroupPartialUpdateInputSerializer(serializers.Serializer):
    bio = serializers.CharField(required=False)
    addIds = serializers.ListField(
        allow_empty=False, required=False, child=serializers.UUIDField()
    )
    removeIds = serializers.ListField(
        allow_empty=False, required=False, child=serializers.UUIDField()
    )
    makeAdminIds = serializers.ListField(
        allow_empty=False, required=False, child=serializers.UUIDField()
    )
    stripAdminIds = serializers.ListField(
        allow_empty=False, required=False, child=serializers.UUIDField()
    )

    def validate_addIds(self, value):
        return validate_no_duplicates(value, "addIds")

    def validate_removeIds(self, value):
        return validate_no_duplicates(value, "removeIds")

    def validate_makeAdminIds(self, value):
        return validate_no_duplicates(value, "makeAdminIds")

    def validate_stripAdminIds(self, value):
        return validate_no_duplicates(value, "stripAdminIds")

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)

        if not data:
            raise serializers.ValidationError("Must update at least one field.")

        return data


class GroupMessageCreateInputSerializer(serializers.Serializer):
    content = serializers.CharField(default="")
    replyToId = serializers.UUIDField(required=False)
    groupId = serializers.UUIDField()
    hasFile = serializers.BooleanField()

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)
        if not data["content"] and not data["hasFile"]:
            raise serializers.ValidationError(
                "Text content and file cannot both be missing."
            )

        return data


class GroupMessagePartialUpdateInputSerializer(serializers.Serializer):
    content = serializers.CharField()
    groupId = serializers.UUIDField()

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)
        return data


class GroupMessageListInputSerializer(serializers.Serializer):
    since = serializers.DateTimeField(required=False)
    groupId = serializers.UUIDField()

    def validate_since(self, value):
        now = timezone.now()
        if value > now:
            raise serializers.ValidationError(
                "The 'since' datetime cannot be in the future."
            )

        one_year_ago = now - timedelta(days=365)
        if value < one_year_ago:
            raise serializers.ValidationError(
                "The 'since' datetime is too far in the past (must be within 1 year)."
            )

        return value

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)
        return data
