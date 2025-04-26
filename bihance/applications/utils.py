import os 
import resend
from .models import Application, User


# Helper functions
def get_employee_applications(employee_id):
    employee_applications = Application.objects.filter(employee_id=employee_id).select_related("job")
    return employee_applications 
    

def get_all_applications(user_id, application_status: int | None): 
    is_employee = User.objects.get(id=user_id).employee

    # Temp workaround, for the fact that employee field may be NULL
    if not is_employee:
        is_employee = True 
    
    if is_employee:
        # Get their applications only 
        queryset = Application.objects.filter(employee_id=user_id).select_related("job")
    else:
        # Get applications to their job only 
        queryset = Application.objects.filter(employer_id=user_id).select_related("job", "user")

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
        "html": f'<p>{message}</p>',
    }

    resend.Emails.send(params)
    

