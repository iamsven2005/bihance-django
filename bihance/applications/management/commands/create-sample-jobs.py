from queue import Full
import uuid
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from datetime import datetime, timezone
from applications.models import Job
from jobs.models import JobRequirement 
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(id="efea8845-d9fa-5031-8f01-9318c6eab8bd")
Job.employer = user

sample_jobs = [
    {
        "job_id": str(uuid.uuid4()),
        "name": "IT Support Assistant",
        "company": "Shopee",
        "location_name": "Mapletree Business City",
        "description": "Provide basic IT troubleshooting and setup assistance.",
        "salary": 2800,
        "higher_salary": 3200,
        "duration": "Contract",
        "start_date": "2025-07-10",
        "end_date": "2026-07-10",
        "job_type": "Contract",
        "pay_type": "Monthly",
        "posted_date": "2025-06-12",
        "gender": None,
        "start_age": 21,
        "end_age": 40,
        "location": None,
        "category": "IT",
        "employer_id": "958bb96d-d4ef-58ce-add9-7e3ab663d775",
    },
]

class Command(BaseCommand):
    help = "Create sample job entries"

    def handle(self, *args, **kwargs):
        for job_data in sample_jobs:
            job, created = Job.objects.get_or_create(
                job_id=job_data["job_id"],
                defaults={
                    "name": job_data["name"],
                    "company": job_data["company"],
                    "location_name": job_data["location_name"],
                    "description": job_data["description"],
                    "salary": job_data["salary"],
                    "higher_salary": job_data.get("higher_salary"),
                    "duration": job_data.get("duration"),
                    "start_date": make_aware(datetime.strptime(job_data["start_date"], "%Y-%m-%d")),
                    "end_date": make_aware(datetime.strptime(job_data["end_date"], "%Y-%m-%d")),
                    "job_type": job_data.get("job_type"),
                    "pay_type": job_data.get("pay_type"),
                    "posted_date": make_aware(datetime.strptime(job_data["posted_date"], "%Y-%m-%d")),
                    "gender": None if job_data.get("gender") == "Any" else job_data.get("gender"),
                    "start_age": job_data.get("start_age"),
                    "end_age": job_data.get("end_age"),
                    "location": job_data.get("location"),
                    "employer_id": User.objects.get(id=job_data.get("employer_id")),
                },
            )

            if created and job_data.get("requirements"):
                for req in job_data["requirements"]:
                    JobRequirement.objects.create(job_id=job, name=req)

        self.stdout.write(self.style.SUCCESS("Sample jobs created successfully."))
