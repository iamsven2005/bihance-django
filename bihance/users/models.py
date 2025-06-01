import uuid

from applications.models import User
from django.db import models


class Interest(models.Model):
    interest_id = models.TextField(
        primary_key=True, db_column="interestId", default=uuid.uuid4, max_length=36
    )
    user_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column="userId")
    name = models.TextField()
    description = models.TextField()

    class Meta:
        db_table = "Interest"
        indexes = [
            models.Index(fields=["user_id"]),
        ]


class Skill(models.Model):
    skill_id = models.TextField(
        primary_key=True, db_column="skillId", default=uuid.uuid4, max_length=36
    )
    user_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column="userId")
    name = models.TextField()

    class Meta:
        db_table = "Skill"
        indexes = [
            models.Index(fields=["user_id"]),
        ]
