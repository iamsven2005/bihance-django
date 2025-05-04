from applications.models import Application, User
from rest_framework.exceptions import NotFound


def get_user_and_application(user_id, application_id):
    # Try to retrieve the user record 
    try: 
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise NotFound("No user corresponding to the message.")
    
    # Try to retrive the application record 
    try: 
        application = Application.objects.get(application_id=application_id)
    except Application.DoesNotExist: 
        raise NotFound("No application corresponding to the message.")
    
    return (user, application)


def validate_user_in_application(user, application): 
    if application.employee_id != user and application.employer_id != user.id: 
        return False
    else: 
        return True
    
def validate_user_is_sender(user, message):
    if message.sender_id != user: 
        return False    
    else: 
        return True
    

