import uuid

from django.db import models

from applications.models import User


class Interest(models.Model):
    interest_id = models.UUIDField(
        primary_key=True, db_column="interestId", default=uuid.uuid4
    )
    user_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column="userId")
    name = models.TextField()
    description = models.TextField()

    class Meta:
        db_table = "Interest"

    def __str__(self):
        return str(self.interest_id)


class Skill(models.Model):
    skill_id = models.UUIDField(
        primary_key=True, db_column="skillId", default=uuid.uuid4
    )
    user_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column="userId")
    name = models.TextField()

    class Meta:
        db_table = "Skill"

    def __str__(self):
        return str(self.skill_id)
