from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone

class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    USER = 'user', 'User'

class JobType(models.TextChoices):
    FULL_TIME = 'FULL_TIME', 'Full Time'
    PART_TIME = 'PART_TIME', 'Part Time'
    CONTRACT = 'CONTRACT', 'Contract'
    TEMPORARY = 'TEMPORARY', 'Temporary'
    INTERNSHIP = 'INTERNSHIP', 'Internship'

class User(AbstractUser):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)
    image_url = models.URLField(null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    employee = models.BooleanField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    role = models.CharField(max_length=10, choices=UserRole.choices, default=UserRole.USER)
    location = models.JSONField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['email']),
        ]

class Job(models.Model):
    job_id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    salary = models.FloatField(null=True, blank=True)
    higher_salary = models.FloatField(null=True, blank=True)
    description = models.TextField()
    requirements = models.TextField(null=True, blank=True)
    posted_date = models.DateTimeField()
    photo_url = models.URLField()
    start_age = models.IntegerField(null=True, blank=True)
    end_age = models.IntegerField(null=True, blank=True)
    gender = models.BooleanField(null=True, blank=True)
    location = models.JSONField(null=True, blank=True)
    job_type = models.CharField(max_length=20, choices=JobType.choices, null=True, blank=True)
    location_name = models.CharField(max_length=255, null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    duration = models.CharField(max_length=255, null=True, blank=True)  # 6months, 1 year
    pay_type = models.CharField(max_length=255, null=True, blank=True)  # hourly, monthly, contract

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['job_type']),
            models.Index(fields=['location_name']),
        ]

class Application(models.Model):
    application_id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    accept = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    bio = models.TextField(null=True, blank=True)
    employee_review = models.TextField(null=True, blank=True)
    employer_review = models.TextField(null=True, blank=True)
    employer_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['job']),
        ]

        