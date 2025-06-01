from applications.serializers import UserSerializer

from .serializers import (
    SuggestionCommentSerializer,
    SuggestionSerializer,
    SuggestionVoteSerializer,
)


def to_json_object_base(suggestion):
    suggestion_serializer = SuggestionSerializer(suggestion)
    suggestion_data = {
        **suggestion_serializer.data,
        "comment_count": suggestion.comment_count,
        "vote_count": suggestion.vote_count,
    }
    user_serializer = UserSerializer(suggestion.author_id)
    data = {"suggestion": suggestion_data, "author": user_serializer.data}

    return data


def to_json_object_list(suggestion):
    data = to_json_object_base(suggestion)
    associated_votes = suggestion.suggestionvote_set.all()
    if associated_votes:
        vote_serializer = SuggestionVoteSerializer(associated_votes, many=True)
        data["votes"] = vote_serializer.data
    else:
        data["votes"] = None

    return data


def to_json_object_retrieve(suggestion):
    data = to_json_object_list(suggestion)
    associated_comments = suggestion.suggestioncomment_set.all()
    if associated_comments:
        comment_serializer = SuggestionCommentSerializer(associated_comments, many=True)
        data["comments"] = comment_serializer.data
    else:
        data["comments"] = None

    return data


def to_json_object_leaderboard(user):
    user_serializer = UserSerializer(user)
    data = {**user_serializer.data}
    if hasattr(user, "implemented_count"):
        data["implemented_count"] = user.implemented_count

    if hasattr(user, "vote_count"):
        data["vote_count"] = user.vote_count

    return data
