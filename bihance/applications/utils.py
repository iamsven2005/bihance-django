import os

from django.conf import settings
from django.core.mail import EmailMessage, get_connection

from .models import Application

base_queryset = Application.objects.select_related(
    "job_id", "employee_id"
).prefetch_related("message_set")


# Helper functions
def get_employee_applications(employee):
    employee_applications = base_queryset.filter(employee_id=employee)
    return employee_applications


def get_all_applications(user, application_status: int | None):
    is_employee = user.employee

    if is_employee:
        # Get their applications only
        queryset = base_queryset.filter(employee_id=user)
    else:
        # Get applications to their jobs only
        queryset = base_queryset.filter(employer_id=user)

    if application_status is not None:
        queryset = queryset.filter(accept=application_status)

    return queryset


def send_email(recipient_list, subject, message):
    from_email = os.getenv("RESEND_FROM_EMAIL")

    with get_connection(
        host=settings.RESEND_SMTP_HOST,
        port=settings.RESEND_SMTP_PORT,
        username=settings.RESEND_SMTP_USERNAME,
        password=os.getenv("RESEND_API_KEY"),
        use_tls=True,
    ) as connection:
        EmailMessage(
            subject=subject,
            body=message,
            to=recipient_list,
            from_email=from_email,
            connection=connection,
        ).send()
