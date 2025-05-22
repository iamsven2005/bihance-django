import os

from django.conf import settings
from django.core.mail import EmailMessage, get_connection

from .models import Application, User

base_queryset = Application.objects.select_related(
    "job_id", "employee_id"
).prefetch_related("message_set")


# Helper functions
def get_employee_applications(employee_id):
    employee_applications = base_queryset.filter(employee_id=employee_id)
    return employee_applications


def get_all_applications(user_id, application_status: int | None):
    is_employee = User.objects.get(id=user_id).employee

    if is_employee:
        # Get their applications only
        queryset = base_queryset.filter(employee_id=user_id)
    else:
        # Get applications to their job only
        queryset = base_queryset.filter(employer_id=user_id)

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
