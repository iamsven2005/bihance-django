from rest_framework import serializers
from utils.utils import detect_extra_fields

from .models import Suggestion, SuggestionComment, SuggestionVote


class SuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suggestion
        fields = [
            "suggestion_id",
            "title",
            "content",
            "created_at",
            "updated_at",
            "author_id",
            "is_useful",
        ]
        depth = 0


class SuggestionCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestionComment
        fields = [
            "comment_id",
            "content",
            "created_at",
            "updated_at",
            "author_id",
            "suggestion_id",
        ]
        depth = 0


class SuggestionVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestionVote
        fields = ["vote_id", "user_id", "suggestion_id", "created_at"]
        depth = 0


class SuggestionListInputSerializer(serializers.Serializer):
    sortBy = serializers.ChoiceField(
        choices=["newest", "oldest", "most-voted", "implemented", "pending"],
        default="newest",
    )
    searchQuery = serializers.CharField(required=False)

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)
        return data


class SuggestionLeaderboardInputSerializer(serializers.Serializer):
    sortBy = serializers.ChoiceField(
        choices=["most-implemented", "most-votes", "newest-member"],
        default="most-implemented",
    )
    searchQuery = serializers.CharField(required=False)

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)
        return data


class SuggestionCreateInputSerializer(serializers.Serializer):
    title = serializers.CharField()
    content = serializers.CharField()

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)
        return data


class SuggestionCommentInputSerializer(serializers.Serializer):
    content = serializers.CharField()

    def validate(self, data):
        detect_extra_fields(self.initial_data, self.fields)
        return data
