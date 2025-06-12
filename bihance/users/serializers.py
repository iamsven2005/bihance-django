from rest_framework import serializers

from utils.utils import detect_extra_fields

from .models import Interest, Skill


class InterestSerializer(serializers.ModelSerializer):
    # Override __init__ to remove excluded fields
    def __init__(self, *args, **kwargs):
        exclude_fields = kwargs.pop("exclude_fields", None)
        super().__init__(*args, **kwargs)

        if exclude_fields:
            for field_name in exclude_fields:
                self.fields.pop(field_name, None)

    class Meta:
        model = Interest
        fields = ["interest_id", "user_id", "name", "description"]
        depth = 0


class SkillSerializer(serializers.ModelSerializer):
    # Override __init__ to remove excluded fields
    def __init__(self, *args, **kwargs):
        exclude_fields = kwargs.pop("exclude_fields", None)
        super().__init__(*args, **kwargs)

        if exclude_fields:
            for field_name in exclude_fields:
                self.fields.pop(field_name, None)

    class Meta:
        model = Skill
        fields = ["skill_id", "user_id", "name"]
        depth = 0


class UserPartialUpdateInputSerializer(serializers.Serializer):
    firstName = serializers.CharField(required=False)
    lastName = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    bio = serializers.CharField(required=False)
    age = serializers.IntegerField(required=False, min_value=13, max_value=69)
    interests = serializers.ListField(
        required=False,
        allow_empty=False,
        child=InterestSerializer(exclude_fields=["interest_id", "user_id"]),
    )
    skills = serializers.ListField(
        required=False,
        allow_empty=False,
        child=SkillSerializer(exclude_fields=["skill_id", "user_id"]),
    )
    toggleRole = serializers.BooleanField(required=False)

    def validate_toggleRole(self, value):
        # Can only be True
        if value is not None and value is False:
            raise serializers.ValidationError("toggleRole field can only be true.")
        return value

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)
        has_role_toggle = "toggleRole" in data

        # Non toggle, update fields
        update_fields = list(
            filter(lambda fieldname: fieldname != "toggleRole", self.fields.keys())
        )
        has_update_details = any(update_field in data for update_field in update_fields)

        # XOR
        if has_role_toggle ^ has_update_details:
            return data
        raise serializers.ValidationError(
            "Can either toggle user role, or update user details, but not both nor neither."
        )


class UserSearchInputSerializer(serializers.Serializer):
    # Skill names only
    skills = serializers.ListField(
        required=False,
        allow_empty=False,
        child=serializers.CharField(),
    )
    name = serializers.CharField(required=False)
    page = serializers.IntegerField(required=False, min_value=1)
    limit = serializers.IntegerField(required=False, min_value=1)

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)
        return data
