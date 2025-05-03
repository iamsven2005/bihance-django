from applications.models import Application, User
from django.http import HttpResponse


def get_sender_and_application(sender_id, application_id):
    # Try to retrieve the sender record 
    try: 
        sender = User.objects.get(id=sender_id)
    except User.DoesNotExist:
        return HttpResponse("No sender corresponding to the message.", status=404)
    
    # Try to retrive the application record 
    try: 
        application = Application.objects.get(application_id=application_id)
    except Application.DoesNotExist: 
        return HttpResponse("No application corresponding to the message.", status=404)
    
    return (sender, application)


def validate_sender(sender, application): 
    if application.employee_id != sender and application.employer_id != sender: 
        return False
    else: 
        return True


    