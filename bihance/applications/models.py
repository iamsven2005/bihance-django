import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class UserRole(models.TextChoices):
    ADMIN = "Admin"
    USER = "User"


class JobType(models.TextChoices):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    TEMPORARY = "TEMPORARY"
    INTERNSHIP = "INTERNSHIP"


class DurationType(models.TextChoices):
    LESS_THAN_1_MONTH = "Less than 1 month"
    ONE_TO_THREE_MONTHS = "1-3 months"
    THREE_TO_SIX_MONTHS = "3-6 months"
    SIX_TO_TWELVE_MONTHS = "6-12 months"
    ONE_PLUS_YEAR = "1+ year"
    ONGOING = "Ongoing"


class PayType(models.TextChoices):
    HOURLY = "Hourly"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    PROJECT_BASED = "Project-based"
    NEGOTIABLE = "Negotiable"


class User(AbstractUser):
    # Updating some defaults from AbstractUser
    id = models.TextField(
        primary_key=True, default=uuid.uuid4, max_length=36, db_column="id"
    )
    first_name = models.TextField(null=True, blank=True, db_column="firstName")
    last_name = models.TextField(null=True, blank=True, db_column="lastName")
    email = models.EmailField(unique=True)

    # Removing some defaults from AbstractUser
    password = None
    last_login = None
    is_superuser = None
    username = None
    is_staff = None
    is_active = None
    date_joined = None

    # Since username is removed
    # Need to point this to another unique field
    USERNAME_FIELD = "id"

    phone = models.TextField(unique=True, null=True, blank=True)
    employee = models.BooleanField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now, db_column="createdAt")
    updated_at = models.DateTimeField(default=timezone.now, db_column="updatedAt")
    role = models.CharField(
        max_length=20, choices=UserRole.choices, default=UserRole.USER
    )
    location = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "User"
        indexes = [
            models.Index(fields=["email"]),
        ]


class Job(models.Model):
    job_id = models.TextField(
        primary_key=True, default=uuid.uuid4, max_length=36, db_column="jobId"
    )
    name = models.CharField(max_length=255, db_column="Name")
    employer_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column="id")

    start_date = models.DateTimeField(db_column="StartDate")
    end_date = models.DateTimeField(null=True, blank=True, db_column="EndDate")
    salary = models.FloatField(null=True, blank=True, db_column="Salary")
    higher_salary = models.FloatField(null=True, blank=True, db_column="HigherSalary")
    description = models.TextField(db_column="Description")
    requirements = models.TextField(null=True, blank=True, db_column="Requirements")

    posted_date = models.DateTimeField(db_column="PostedDate")
    start_age = models.IntegerField(null=True, blank=True, db_column="Startage")
    end_age = models.IntegerField(null=True, blank=True, db_column="Endage")

    # True -> Female, # False -> Male
    gender = models.BooleanField(null=True, blank=True, db_column="Gender")

    location = models.JSONField(null=True, blank=True)
    job_type = models.CharField(
        choices=JobType.choices, null=True, blank=True, db_column="jobType"
    )
    location_name = models.TextField(null=True, blank=True, db_column="locationName")
    company = models.TextField(null=True, blank=True, db_column="Company")
    duration = models.TextField(
        choices=DurationType.choices, null=True, blank=True, db_column="Duration"
    )
    pay_type = models.TextField(
        choices=PayType.choices, null=True, blank=True, db_column="PayType"
    )

    class Meta:
        db_table = "Job"
        indexes = [
            models.Index(fields=["employer_id"]),
            models.Index(fields=["job_type"]),
            models.Index(fields=["location_name"]),
        ]
        unique_together = ("name", "employer_id", "start_date")


class Application(models.Model):
    application_id = models.TextField(
        primary_key=True, default=uuid.uuid4, max_length=36, db_column="applicationId"
    )
    job_id = models.ForeignKey(Job, on_delete=models.DO_NOTHING, db_column="jobId")
    accept = models.IntegerField()
    employee_id = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        db_column="id",
        related_name="applications_as_employee",
    )
    employer_id = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        db_column="employerId",
        related_name="appications_as_employer",
    )

    bio = models.TextField(null=True, blank=True, db_column="Bio")
    employee_review = models.TextField(
        null=True, blank=True, db_column="EmployeeReview"
    )
    employer_review = models.TextField(
        null=True, blank=True, db_column="EmployerReview"
    )

    class Meta:
        db_table = "Application"
        indexes = [
            models.Index(fields=["job_id"]),
            models.Index(fields=["employee_id"]),
            models.Index(fields=["employer_id"]),
        ]
        unique_together = ("job_id", "employee_id")
