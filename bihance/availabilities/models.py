import uuid 

from applications.models import User
from django.db import models


class Timings(models.Model):
    time_id = models.TextField(primary_key=True, default=uuid.uuid4, max_length=36, db_column='timeId')  
    start_time = models.DateTimeField(db_column='Starttime')  
    end_time = models.DateTimeField(db_column='Endtime')  
    employee_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='id')
    title = models.TextField(db_column='Title', blank=True, null=True)  

    class Meta:
        db_table = 'timings'
        indexes = [
            models.Index(fields=['employee_id']),
        ]