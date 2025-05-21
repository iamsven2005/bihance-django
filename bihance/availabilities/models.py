import uuid 

from applications.models import User
from django.db import models


class Timing(models.Model):
    time_id = models.TextField(primary_key=True, default=uuid.uuid4, max_length=36, db_column='timeId')  
    start_time = models.DateTimeField(db_column='Starttime')  
    end_time = models.DateTimeField(db_column='Endtime')  
    employee_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='id')
    title = models.TextField(blank=True, null=True, db_column='Title')  

    class Meta:
        db_table = 'Timing'
        indexes = [
            models.Index(fields=['employee_id']),
        ]

        unique_together = (('start_time', 'end_time', "employee_id"))


        