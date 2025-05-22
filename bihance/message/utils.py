def validate_user_is_sender(user, message):
    if message.sender_id != user:
        return False
    else:
        return True
