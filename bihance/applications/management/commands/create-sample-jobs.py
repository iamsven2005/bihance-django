import uuid
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from datetime import datetime
from applications.models import Job
from jobs.models import JobRequirement
from django.contrib.auth import get_user_model

User = get_user_model()

sample_jobs = [
    {
        "name": "Prompt Engineer",
        "company": "OpenAI",
        "location_name": "Mapletree Business City",
        "description": "Join OpenAI as a Prompt Engineer to develop and refine AI models. You will work closely with our research team to create effective prompts that enhance model performance. Ideal candidates should have a strong understanding of LLMs, Python programming skills, and experience in crafting prompts for AI systems.",
        "salary": 5000,
        "higher_salary": 5500,
        "duration": "Full-time",
        "start_date": "2025-07-11",
        "end_date": "2099-12-31",
        "job_type": "FULL_TIME",
        "pay_type": "Monthly",
        "posted_date": "2025-06-12",
        "gender": None,
        "start_age": 21,
        "end_age": 40,
        "location": {"lat": 1.3521, "lng": 103.8198},
        "category": "IT",
        "employer_id": "958bb96d-d4ef-58ce-add9-7e3ab663d775",
        "job_requirements": ["LLM understanding", "Python", "Prompting skills"],
    },
]

class Command(BaseCommand):
    help = "Seeds the development database with job listings"

    def handle(self, *args, **kwargs):
        for job_data in sample_jobs:
            employer = User.objects.get(id=job_data["employer_id"])

            job = Job.objects.create(
                job_id=uuid.uuid4(),
                name=job_data["name"],
                company=job_data["company"],
                location_name=job_data["location_name"],
                description=job_data["description"],
                salary=job_data["salary"],
                higher_salary=job_data["higher_salary"],
                duration=job_data["duration"],
                start_date=make_aware(datetime.strptime(job_data["start_date"], "%Y-%m-%d")),
                end_date=make_aware(datetime.strptime(job_data["end_date"], "%Y-%m-%d")),
                job_type=job_data["job_type"],
                pay_type=job_data["pay_type"],
                posted_date=make_aware(datetime.strptime(job_data["posted_date"], "%Y-%m-%d")),
                gender=job_data["gender"],
                start_age=job_data["start_age"],
                end_age=job_data["end_age"],
                location=job_data["location"],
                category=job_data["category"],
                employer_id=employer,
            )

            for req in job_data.get("job_requirements", []):
                JobRequirement.objects.create(name=req, job_id=job)

            self.stdout.write(f"✅ Created job: {job.name} ({job.job_id})")

        self.stdout.write(self.style.SUCCESS("🎉 All jobs created successfully."))
