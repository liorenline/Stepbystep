

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models.user  import User
from app.models.verification import EmailCode
from app.forms.auth_forms    import (
    RegistrationForm, LoginForm, VerifyCodeForm,
    ResetPasswordRequestForm, ResetPasswordForm,
    ChangePasswordForm, ChangeEmailForm,
)
from app.services.email_service import (
    send_verification_code, send_2fa_code,
    send_reset_password_code, send_change_password_code,
    send_change_email_code
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        code_obj = EmailCode.generate(user.id, "verify_email")
        send_verification_code(user.email, code_obj.code)

        session["verify_email"] = user.email
        flash("Account created! Check your email for the verification code.", "success")
        return redirect(url_for("auth.verify_email"))

    return render_template("register.html", form=form)

@auth_bp.route("/verify-email", methods=["GET", "POST"])
def verify_email():
    email = session.get("verify_email")
    if not email:
        return redirect(url_for("auth.register"))

    user = User.query.filter_by(email=email).first_or_404()
    form = VerifyCodeForm()

    if form.validate_on_submit():
        code_obj = EmailCode.query.filter_by(
            user_id=user.id, purpose="verify_email", is_used=False
        ).order_by(EmailCode.created_at.desc()).first()

        if not code_obj or not code_obj.is_valid():
            flash("Code expired. Request a new one.", "danger")
        elif code_obj.code != form.code.data:
            flash("Wrong code. Try again.", "danger")
        else:
            code_obj.mark_used()
            user.is_verified = True
            db.session.commit()
            session.pop("verify_email", None)
            flash("Email confirmed! You can now log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("verify_email.html", form=form, email=email)


@auth_bp.route("/resend-verification")
def resend_verification():
    email = session.get("verify_email")
    if email:
        user = User.query.filter_by(email=email).first()
        if user and not user.is_verified:
            code_obj = EmailCode.generate(user.id, "verify_email")
            send_verification_code(user.email, code_obj.code)
            flash("New code sent.", "info")
    return redirect(url_for("auth.verify_email"))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if not user or not user.check_password(form.password.data):
            flash("Wrong email or password.", "danger")
            return render_template("login.html", form=form)

        if not user.is_verified:
            session["verify_email"] = user.email
            flash("Please verify your email first.", "warning")
            return redirect(url_for("auth.verify_email"))

        if user.is_2fa_enabled:
            code_obj = EmailCode.generate(user.id, "two_factor")
            send_2fa_code(user.email, code_obj.code)
            session["2fa_user_id"] = user.id
            session["2fa_remember"] = form.remember_me.data
            return redirect(url_for("auth.two_factor"))

        login_user(user, remember=form.remember_me.data)
        flash(f"Welcome back, {user.username}!", "success")
        next_page = request.args.get("next")
        return redirect(next_page or url_for("main.dashboard"))

    return render_template("login.html", form=form)

@auth_bp.route("/two-factor", methods=["GET", "POST"])
def two_factor():
    user_id = session.get("2fa_user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    user = User.query.get_or_404(user_id)
    form = VerifyCodeForm()

    if form.validate_on_submit():
        code_obj = EmailCode.query.filter_by(
            user_id=user_id, purpose="two_factor", is_used=False
        ).order_by(EmailCode.created_at.desc()).first()

        if not code_obj or not code_obj.is_valid():
            flash("Code expired. Please log in again.", "danger")
            return redirect(url_for("auth.login"))
        if code_obj.code != form.code.data:
            flash("Wrong code.", "danger")
        else:
            code_obj.mark_used()
            remember = session.pop("2fa_remember", False)
            session.pop("2fa_user_id", None)
            login_user(user, remember=remember)
            flash(f"Welcome, {user.username}!", "success")
            return redirect(url_for("main.dashboard"))

    return render_template("two_factor.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))

@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password_request():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            code_obj = EmailCode.generate(user.id, "reset_password")
            send_reset_password_code(user.email, code_obj.code)
        # Always show the same message to avoid revealing whether an email exists
        flash("If that email is registered you will receive a reset code.", "info")
        session["reset_email"] = form.email.data.lower()
        return redirect(url_for("auth.reset_password_confirm"))
    return render_template("reset_password_request.html", form=form)


@auth_bp.route("/reset-password/confirm", methods=["GET", "POST"])
def reset_password_confirm():
    email = session.get("reset_email")
    if not email:
        return redirect(url_for("auth.reset_password_request"))

    user = User.query.filter_by(email=email).first()
    form = ResetPasswordForm()

    if form.validate_on_submit():
        code_obj = EmailCode.query.filter_by(
            user_id=user.id, purpose="reset_password", is_used=False
        ).order_by(EmailCode.created_at.desc()).first()

        if not code_obj or not code_obj.is_valid():
            flash("Code expired. Request a new one.", "danger")
        elif code_obj.code != form.code.data:
            flash("Wrong code.", "danger")
        else:
            code_obj.mark_used()
            user.set_password(form.password.data)
            db.session.commit()
            session.pop("reset_email", None)
            flash("Password changed! You can now log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("reset_password.html", form=form)

@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()

    # Send the code on GET
    if request.method == "GET":
        code_obj = EmailCode.generate(current_user.id, "change_password")
        send_change_password_code(current_user.email, code_obj.code)
        flash("A confirmation code was sent to your email.", "info")

    if form.validate_on_submit():
        code_obj = EmailCode.query.filter_by(
            user_id=current_user.id, purpose="change_password", is_used=False
        ).order_by(EmailCode.created_at.desc()).first()

        if not code_obj or not code_obj.is_valid():
            flash("Code expired. Reload the page to get a new one.", "danger")
        elif code_obj.code != form.code.data:
            flash("Wrong code.", "danger")
        else:
            code_obj.mark_used()
            current_user.set_password(form.password.data)
            db.session.commit()
            flash("Password updated!", "success")
            return redirect(url_for("main.profile"))

    return render_template("change_password.html", form=form)

@auth_bp.route("/change-email", methods=["GET", "POST"])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        new_email = form.new_email.data.lower()
        code_obj = EmailCode.generate(current_user.id, "change_email", new_email=new_email)
        send_change_email_code(new_email, code_obj.code)
        session["pending_email"] = new_email
        flash(f"A code was sent to {new_email}.", "info")
        return redirect(url_for("auth.change_email_confirm"))
    return render_template("change_email.html", form=form)


@auth_bp.route("/change-email/confirm", methods=["GET", "POST"])
@login_required
def change_email_confirm():
    form = VerifyCodeForm()
    if form.validate_on_submit():
        code_obj = EmailCode.query.filter_by(
            user_id=current_user.id, purpose="change_email", is_used=False
        ).order_by(EmailCode.created_at.desc()).first()

        if not code_obj or not code_obj.is_valid():
            flash("Code expired. Start again.", "danger")
            return redirect(url_for("auth.change_email_request"))
        if code_obj.code != form.code.data:
            flash("Wrong code.", "danger")
        else:
            code_obj.mark_used()
            current_user.email = code_obj.new_email
            db.session.commit()
            session.pop("pending_email", None)
            flash("Email updated!", "success")
            return redirect(url_for("main.profile"))
    return render_template("change_email_confirm.html", form=form)
