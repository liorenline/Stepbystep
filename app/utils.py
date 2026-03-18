from flask import current_app
from flask_mail import Message
from app.extensions import mail


def send_email(to, subject, body):
    msg = Message(
        subject=subject,
        recipients=[to],
        body=body,
    )
    mail.send(msg)


def send_verification_code(user, code, purpose):
    subjects = {
        "register": "Step by Step — Confirm your email",
        "2fa": "Step by Step — Login verification code",
        "reset_password": "Step by Step — Reset your password",
        "change_password": "Step by Step — Confirm password change",
        "change_email": "Step by Step — Confirm your new email",
    }
    messages = {
        "register": f"Welcome to Step by Step!\n\nYour confirmation code: {code}\n\nIt expires in 15 minutes.",
        "2fa": f"Your login verification code: {code}\n\nIt expires in 15 minutes.",
        "reset_password": f"Your password reset code: {code}\n\nIt expires in 15 minutes.",
        "change_password": f"Your password change confirmation code: {code}\n\nIt expires in 15 minutes.",
        "change_email": f"Your email change confirmation code: {code}\n\nIt expires in 15 minutes.",
    }
    send_email(
        to=user.email,
        subject=subjects.get(purpose, "Step by Step — Verification code"),
        body=messages.get(purpose, f"Your code: {code}"),
    )


def validate_password_strength(password):
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter.")
    special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
    if not any(c in special_chars for c in password):
        errors.append("Password must contain at least one special character.")
    return errors
