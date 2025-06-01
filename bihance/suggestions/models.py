import uuid

from applications.models import User
from django.db import models
from django.utils import timezone


class Suggestion(models.Model):
    suggestion_id = models.TextField(
        primary_key=True, db_column="suggestionId", default=uuid.uuid4, max_length=36
    )
    title = models.TextField()
    content = models.TextField()
    created_at = models.DateTimeField(db_column="createdAt", default=timezone.now)
    updated_at = models.DateTimeField(db_column="updatedAt", default=timezone.now)
    author_id = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, db_column="authorId"
    )
    is_useful = models.BooleanField(db_column="isUseful", default=False)

    class Meta:
        db_table = "Suggestion"
        indexes = [
            models.Index(fields=["author_id"]),
        ]


class SuggestionComment(models.Model):
    comment_id = models.TextField(
        primary_key=True, db_column="commentId", default=uuid.uuid4, max_length=36
    )
    content = models.TextField()
    created_at = models.DateTimeField(db_column="createdAt", default=timezone.now)
    updated_at = models.DateTimeField(db_column="updatedAt", default=timezone.now)
    author_id = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, db_column="authorId"
    )
    suggestion_id = models.ForeignKey(
        Suggestion, on_delete=models.DO_NOTHING, db_column="suggestionId"
    )

    class Meta:
        db_table = "Suggestion_Comment"
        indexes = [
            models.Index(fields=["author_id"]),
            models.Index(fields=["suggestion_id"]),
        ]


class SuggestionVote(models.Model):
    vote_id = models.TextField(
        primary_key=True, db_column="voteId", default=uuid.uuid4, max_length=36
    )
    user_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column="userId")
    suggestion_id = models.ForeignKey(
        Suggestion, on_delete=models.DO_NOTHING, db_column="suggestionId"
    )
    created_at = models.DateTimeField(db_column="createdAt", default=timezone.now)

    class Meta:
        db_table = "Suggestion_Vote"
        unique_together = (("user_id", "suggestion_id"),)
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["suggestion_id"]),
        ]
