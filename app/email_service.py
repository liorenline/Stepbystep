
from flask import current_app
from flask_mail import Message
from app import mail


def _send(to, subject, text):
    try:
        msg = Message(subject=subject, recipients=[to], body=text)
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Email error → {to}: {e}")
        return False


def send_verification_code(email, code):
    return _send(
        email,
        "Step by Step — Verify your account",
        f"Your verification code: {code}\n\nValid for 15 minutes."
    )


def send_2fa_code(email, code):
    return _send(
        email,
        "Step by Step — Login code",
        f"Your login code: {code}\n\nValid for 15 minutes."
    )


def send_reset_password_code(email, code):
    return _send(
        email,
        "Step by Step — Reset password",
        f"Your password reset code: {code}\n\nValid for 15 minutes."
    )


def send_change_password_code(email, code):
    return _send(
        email,
        "Step by Step — Change password",
        f"Your confirmation code: {code}\n\nValid for 15 minutes."
    )


def send_change_email_code(new_email, code):
    return _send(
        new_email,
        "Step by Step — Confirm new email",
        f"Your confirmation code: {code}\n\nValid for 15 minutes."
    )
