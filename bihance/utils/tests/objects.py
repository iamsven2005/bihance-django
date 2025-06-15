from datetime import datetime

from applications.models import Application, Job, User
from django.utils.timezone import make_aware
from message.models import Message
from suggestions.models import Suggestion
from users.models import Interest, Skill


def get_employee():
    employee, _ = User.objects.get_or_create(
        first_name="John",
        last_name="Doe",
        email="employee@gmail.com",
        employee=True,
        role="Admin",
    )
    return employee


def get_employer():
    employer, _ = User.objects.get_or_create(
        first_name="Nick",
        last_name="Girl",
        email="employer@gmail.com",
        employee=False,
    )
    return employer


def create_employee_skills():
    employee = get_employee()
    Skill.objects.create(user_id=employee, name="Python")
    Skill.objects.create(user_id=employee, name="C++")
    Skill.objects.create(user_id=employee, name="Rust")


def create_employee_interests():
    employee = get_employee()
    Interest.objects.create(
        user_id=employee,
        name="Badminton",
        description="I love to SMASH (shuttle)cocks.",
    )
    Interest.objects.create(
        user_id=employee, name="Piano", description="I love to FINGER minor(keys)."
    )


def create_employee_suggestion():
    employee = get_employee()
    Suggestion.objects.create(
        title="My First Suggestion",
        content="This website abit laggy, please make it load faster!",
        author_id=employee,
    )


def get_job():
    FIXED_DATE = make_aware(datetime(2025, 1, 1, 12, 0, 0))

    job, _ = Job.objects.get_or_create(
        name="Forest Guardian & Glitch Hunter",
        employer_id=get_employer(),
        start_date=FIXED_DATE,
        description="Must be able to transform into a tree, detect glitch entities.",
        posted_date=FIXED_DATE,
    )
    return job


def get_application():
    application, _ = Application.objects.get_or_create(
        job_id=get_job(),
        accept=1,
        employee_id=get_employee(),
        employer_id=get_employer(),
    )
    return application


# Not a group message btw
def get_message():
    message, _ = Message.objects.get_or_create(
        content="Hello World",
        application_id=get_application(),
        sender_id=get_employee(),
    )
    return message
