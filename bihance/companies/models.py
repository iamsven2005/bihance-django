import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from applications.models import User


class EmployerProfile(models.Model):
    company_id = models.TextField(primary_key=True, default=uuid.uuid4, max_length=36, db_column="id")
    employer_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='userId')  
    company_name = models.TextField(db_column='companyName')  
    company_website = models.URLField(db_column='companyWebsite')  
    contact_name = models.TextField(null=True, blank=True, db_column='contactName')  
    contact_role = models.TextField(null=True, blank=True, db_column='contactRole')  
    company_size = models.TextField(null=True, blank=True, db_column='companySize')  
    industry = models.TextField(null=True, blank=True)

    # Accepted values would be of the form [str1, str2, str3]
    talent_needs = ArrayField(models.TextField(), null=True, blank=True, db_column='talentNeeds')
    work_style = ArrayField(models.TextField(), null=True, blank=True, db_column='workStyle')

    hiring_timeline = models.TextField(null=True, blank=True, db_column='hiringTimeline')
    featured_partner = models.BooleanField(default=False, db_column='featuredPartner')  
    created_at = models.DateTimeField(default=timezone.now, db_column='createdAt')  
    updated_at = models.DateTimeField(default=timezone.now, db_column='updatedAt')  

    class Meta:
        db_table = 'EmployerProfile'
        indexes = [
            models.Index(fields=['employer_id']),
        ]

        unique_together = (('employer_id', 'company_name', 'company_website'))


class CompanyFollow(models.Model):
    follow_id = models.TextField(primary_key=True, default=uuid.uuid4, max_length=36, db_column="id")
    follower_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='userId')  
    company_id = models.ForeignKey(EmployerProfile, on_delete=models.DO_NOTHING, db_column='companyId')  
    created_at = models.DateTimeField(default=timezone.now, db_column='createdAt')  

    class Meta:
        db_table = 'companyFollow'
        indexes = [
            models.Index(fields=['follower_id']),
            models.Index(fields=['company_id']),
            models.Index(fields=['follower_id', 'company_id'])
        ]

        unique_together = (('follower_id', 'company_id'))


