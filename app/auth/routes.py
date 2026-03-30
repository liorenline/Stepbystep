from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.extensions import db
from app.models import User, EmailCode
from app.forms import (
    RegistrationForm,
    LoginForm,
    VerifyCodeForm,
    ResetPasswordRequestForm,
    ResetPasswordForm,
    ChangePasswordForm,
    ChangeEmailForm,
)
from app.utils import send_verification_code
