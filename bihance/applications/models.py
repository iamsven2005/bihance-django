import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractUser
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
    user_id = models.TextField(primary_key=True, default=uuid.uuid4, max_length=36, db_column="id")
    first_name = models.TextField(null=True, blank=True, db_column="firstName")
    last_name = models.TextField(null=True, blank=True, db_column="lastName")
    email = models.EmailField(unique=True)
    image_url = models.URLField(null=True, blank=True, db_column="imageUrl")
    phone = models.TextField(unique=True, null=True, blank=True)

    employee = models.BooleanField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now, db_column="createdAt")
    updated_at = models.DateTimeField(default=timezone.now, db_column="updatedAt")
    role = models.TextField(choices=UserRole, default=UserRole.USER)
    location = models.JSONField(null=True, blank=True)
    # Array fields ignored for now 

    class Meta:
        db_table = "user"
        managed = False
        indexes = [
            models.Index(fields=['email']),
        ]


class Job(models.Model):
    job_id = models.TextField(primary_key=True, default=uuid.uuid4, max_length=36, db_column="jobId")
    name = models.CharField(max_length=255, db_column="Name")
    employer_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="id")

    start_date = models.DateTimeField(db_column="StartDate")
    end_date = models.DateTimeField(null=True, blank=True, db_column="EndDate")
    salary = models.FloatField(null=True, blank=True, db_column="Salary")
    higher_salary = models.FloatField(null=True, blank=True, db_column="HigherSalary")
    description = models.TextField(db_column="Description")
    requirements = models.TextField(null=True, blank=True, db_column="Requirements")

    posted_date = models.DateTimeField(db_column="PostedDate")
    photo_url = models.URLField(db_column="PhotoUrl")
    start_age = models.IntegerField(null=True, blank=True, db_column="Startage")
    end_age = models.IntegerField(null=True, blank=True, db_column="Endage")
    gender = models.BooleanField(null=True, blank=True, db_column="Gender")

    location = models.JSONField(null=True, blank=True)
    job_type = models.TextField(choices=JobType, null=True, blank=True, db_column="jobType")
    location_name = models.TextField(null=True, blank=True, db_column="locationName")
    company = models.TextField(null=True, blank=True, db_column="Company")
    duration = models.TextField(null=True, blank=True, db_column="Duration")  # 6months, 1 year
    pay_type = models.TextField(null=True, blank=True, db_column="PayType")  # hourly, monthly, contract
    # Array fields ignored for now 

    class Meta:
        db_table = "Job"
        managed = False
        indexes = [
            models.Index(fields=['employer_id']),
            models.Index(fields=['job_type']),
            models.Index(fields=['location_name']),
        ]


class Application(models.Model):
    application_id = models.TextField(primary_key=True, default=uuid.uuid4, max_length=36, db_column="applicationId")
    job_id = models.ForeignKey(Job, on_delete=models.CASCADE, db_column="jobId")
    accept = models.IntegerField()
    employee_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="id")
    bio = models.TextField(null=True, blank=True, db_column="Bio")
    employee_review = models.TextField(null=True, blank=True, db_column="EmployeeReview")
    employer_review = models.TextField(null=True, blank=True, db_column="EmployerReview")
    employer_id = models.TextField(null=True, blank=True, db_column="employerId")
    # Array fields ignored for now 

    class Meta:
        db_table = "application"
        managed = False
        indexes = [
            models.Index(fields=['job_id']),
            models.Index(fields=['employee_id']),
        ]


