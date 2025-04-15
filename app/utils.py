from functools import wraps
from flask import current_app
from flask_jwt_extended import get_jwt_identity
from flask_mail import Mail, Message
from app.models import User

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return {"message": "Admin access required"}, 403
        return fn(*args, **kwargs)
    return wrapper

def send_confirmation_email(event, user):
    subject = f"You're Registered for {event.title}!"
    body = f"""
    Hi {user.username},

    You have successfully registered for the event:
    
    Title: {event.title}
    Date: {event.date}
    Location: {event.location}

    Thank you!
    """

    msg = Message(subject, recipients=[user.email], body=body)
    
    with current_app.app_context():
        Mail.send(msg)
