import os 
import resend
from .models import Application, User


# Helper functions
def get_user_applications(employee_id):
    user_applications = Application.objects.filter(user=employee_id).select_related("job")
    return user_applications 
    

def get_all_applications(user_id, application_status): 
    is_employee = User.objects.get(id=user_id).employee

    if is_employee:
        # Get their applications only 
        queryset = Application.objects.filter(user=user_id).select_related("job")
    else:
        # Get applications to their job only 
        queryset = Application.objects.filter(job=user_id).select_related("job", "user")

    if application_status is not None:
        queryset = queryset.filter(accept=application_status)

    return queryset


def send_email(to, subject, message): 
    from_email = os.getenv("RESEND_FROM_EMAIL")
    resend.api_key = os.getenv("RESEND_API_KEY")

    # "to" expects a list of string emails
    params: resend.Emails.SendParams = {
        "from": from_email,
        "to": to,
        "subject": subject,
        "html": message,
    }

    resend.Emails.send(params)
    

