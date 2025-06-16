import uuid

from applications.models import User
from django.db import models
from django.utils import timezone


class Suggestion(models.Model):
    suggestion_id = models.UUIDField(
        primary_key=True, db_column="suggestionId", default=uuid.uuid4
    )
    title = models.TextField()
    content = models.TextField()
    created_at = models.DateTimeField(db_column="createdAt", default=timezone.now)
    updated_at = models.DateTimeField(db_column="updatedAt", default=timezone.now)
    author_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="authorId")
    is_useful = models.BooleanField(db_column="isUseful", default=False)

    class Meta:
        db_table = "Suggestion"

    def __str__(self):
        return str(self.suggestion_id)


class SuggestionComment(models.Model):
    comment_id = models.UUIDField(
        primary_key=True, db_column="commentId", default=uuid.uuid4
    )
    content = models.TextField()
    created_at = models.DateTimeField(db_column="createdAt", default=timezone.now)
    updated_at = models.DateTimeField(db_column="updatedAt", default=timezone.now)
    author_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="authorId")
    suggestion_id = models.ForeignKey(
        Suggestion, on_delete=models.CASCADE, db_column="suggestionId"
    )

    class Meta:
        db_table = "Suggestion_Comment"


class SuggestionVote(models.Model):
    vote_id = models.UUIDField(primary_key=True, db_column="voteId", default=uuid.uuid4)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="userId")
    suggestion_id = models.ForeignKey(
        Suggestion, on_delete=models.CASCADE, db_column="suggestionId"
    )
    created_at = models.DateTimeField(db_column="createdAt", default=timezone.now)

    class Meta:
        db_table = "Suggestion_Vote"
        unique_together = (("user_id", "suggestion_id"),)

    def __str__(self):
        return str(self.vote_id)
