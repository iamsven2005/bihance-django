import uuid

from applications.models import Job
from django.db import models


class JobRequirement(models.Model):
    requirement_id = models.TextField(
        primary_key=True, default=uuid.uuid4, max_length=36, db_column="id"
    )
    name = models.TextField()
    job_id = models.ForeignKey(Job, on_delete=models.DO_NOTHING, db_column="jobId")

    class Meta:
        db_table = "Job_Requirement"
        indexes = [
            models.Index(fields=["job_id"]),
        ]
