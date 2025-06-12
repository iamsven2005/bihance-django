import uuid

from django.db import models

from applications.models import User


class Timing(models.Model):
    time_id = models.UUIDField(primary_key=True, default=uuid.uuid4, db_column="timeId")
    start_time = models.DateTimeField(db_column="startTime")
    end_time = models.DateTimeField(db_column="endTime")
    employee_id = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, db_column="employeeId"
    )
    title = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "Timing"
        unique_together = ("start_time", "end_time", "employee_id")

    def __str__(self):
        return str(self.time_id)
