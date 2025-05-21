from applications.models import Application, Job, User
from message.models import Message
from datetime import datetime
from django.utils.timezone import make_aware


def get_employee(): 
    employee, _ = User.objects.get_or_create(
        id="user_2wGGKihK36mWtgSzXpMoPYyLulX",
        email="employee@gmail.com",
        employee=True
    )
    return employee


def get_employer(): 
    employer, _ = User.objects.get_or_create(
        id="user_2w9owsASS9O50XlIGdFubAjr8x0",
        email="employer@gmail.com",
        employee=False
    )
    return employer


def get_job(): 
    FIXED_DATE = make_aware(datetime(2025, 1, 1, 12, 0, 0))
    
    job, _ = Job.objects.get_or_create(
        job_id="cma20egbu0007145n7evi1u6d", 
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
        employer_id=get_employer().id
    )
    return application


def get_message(): 
    message, _ = Message.objects.get_or_create(
        content="Hello World", 
        application_id = get_application(),
        sender_id = get_employee(),
    )
    return message


