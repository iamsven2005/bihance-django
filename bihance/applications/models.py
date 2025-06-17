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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, db_column="userId")
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

    def __str__(self):
        return str(self.id)


class Job(models.Model):
    job_id = models.UUIDField(primary_key=True, default=uuid.uuid4, db_column="jobId")
    name = models.TextField(max_length=255)
    employer_id = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column="employerId"
    )

    start_date = models.DateTimeField(db_column="startDate")
    end_date = models.DateTimeField(null=True, blank=True, db_column="endDate")
    salary = models.FloatField(null=True, blank=True)
    higher_salary = models.FloatField(null=True, blank=True, db_column="higherSalary")
    description = models.TextField()
    requirements = models.TextField(null=True, blank=True)

    posted_date = models.DateTimeField(db_column="postedDate")
    start_age = models.IntegerField(null=True, blank=True, db_column="startage")
    end_age = models.IntegerField(null=True, blank=True, db_column="endage")

    category = models.CharField(max_length=100, null=True, blank=True)

    # True -> Female, # False -> Male
    gender = models.BooleanField(null=True, blank=True)

    location = models.JSONField(null=True, blank=True)
    job_type = models.CharField(
        choices=JobType.choices, null=True, blank=True, db_column="jobType"
    )
    location_name = models.TextField(null=True, blank=True, db_column="locationName")
    company = models.TextField(null=True, blank=True)
    duration = models.TextField(choices=DurationType.choices, null=True, blank=True)
    pay_type = models.CharField(
        choices=PayType.choices, null=True, blank=True, db_column="payType"
    )

    class Meta:
        db_table = "Job"
        # Note, Django automatically creates index for FK
        indexes = [
            models.Index(fields=["job_type"]),
            models.Index(fields=["location_name"]),
        ]
        unique_together = ("name", "employer_id", "start_date")

    def __str__(self):
        return str(self.job_id)


class Application(models.Model):
    application_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, db_column="applicationId"
    )
    job_id = models.ForeignKey(Job, on_delete=models.CASCADE, db_column="jobId")
    accept = models.IntegerField()
    employee_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="employeeId",
        related_name="applications_as_employee",
    )
    employer_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="employerId",
        related_name="appications_as_employer",
    )

    bio = models.TextField(null=True, blank=True)
    employee_review = models.TextField(
        null=True, blank=True, db_column="employeeReview"
    )
    employer_review = models.TextField(
        null=True, blank=True, db_column="employerReview"
    )

    class Meta:
        db_table = "Application"
        unique_together = ("job_id", "employee_id")

    def __str__(self):
        return str(self.application_id)
