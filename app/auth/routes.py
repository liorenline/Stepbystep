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

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegistrationForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower()).first()
        if existing:
            flash("An account with this email already exists.", "danger")
            return render_template("auth/register.html", form=form)

        user = User(username=form.username.data, email=form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        code = EmailCode.create_for_user(user, purpose="register")
        send_verification_code(user, code.code, purpose="register")

        session["verify_user_id"] = user.id
        flash("Account created! Please check your email for a verification code.", "info")
        return redirect(url_for("auth.verify_email"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/verify-email", methods=["GET", "POST"])
def verify_email():
    user_id = session.get("verify_user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)
    if not user:
        return redirect(url_for("auth.login"))

    form = VerifyCodeForm()
    if form.validate_on_submit():
        code_record = EmailCode.query.filter_by(
            user_id=user.id, purpose="register", is_used=False
        ).order_by(EmailCode.created_at.desc()).first()

        if not code_record or not code_record.is_valid() or code_record.code != form.code.data:
            flash("Invalid or expired code. Please try again.", "danger")
            return render_template("auth/verify_email.html", form=form)

        code_record.is_used = True
        user.is_verified = True
        db.session.commit()

        session.pop("verify_user_id", None)
        login_user(user)
        flash("Email verified! Welcome to Step by Step.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("auth/verify_email.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if not user or not user.check_password(form.password.data):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", form=form)

        if not user.is_verified:
            session["verify_user_id"] = user.id
            code = EmailCode.create_for_user(user, purpose="register")
            send_verification_code(user, code.code, purpose="register")
            flash("Please verify your email first.", "warning")
            return redirect(url_for("auth.verify_email"))

        if user.two_fa_enabled:
            session["2fa_user_id"] = user.id
            code = EmailCode.create_for_user(user, purpose="2fa")
            send_verification_code(user, code.code, purpose="2fa")
            return redirect(url_for("auth.verify_2fa"))

        login_user(user)
        flash("Welcome back!", "success")
        next_page = request.args.get("next")
        return redirect(next_page or url_for("main.dashboard"))

    return render_template("auth/login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))