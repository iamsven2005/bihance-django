import os 
from .models import Application, User
from django.conf import settings
from django.core.mail import EmailMessage, get_connection


# Helper functions
def get_employee_applications(employee_id):
    employee_applications = Application.objects.filter(employee_id=employee_id)
    return employee_applications 
    

def get_all_applications(user_id, application_status: int | None): 
    is_employee = User.objects.get(id=user_id).employee

    # Temp workaround, for the fact that employee field may be NULL
    if not is_employee:
        is_employee = True 
    
    if is_employee:
        # Get their applications only 
        queryset = Application.objects.filter(employee_id=user_id)
    else:
        # Get applications to their job only 
        queryset = Application.objects.filter(employer_id=user_id)

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
            connection=connection
        ).send()
        

    