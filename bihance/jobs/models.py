import uuid

from applications.models import Job
from django.db import models


class JobRequirement(models.Model):
    requirement_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, db_column="requirementId"
    )
    name = models.TextField()
    job_id = models.ForeignKey(Job, on_delete=models.CASCADE, db_column="jobId")

    class Meta:
        db_table = "Job_Requirement"

    def __str__(self):
        return str(self.requirement_id)
