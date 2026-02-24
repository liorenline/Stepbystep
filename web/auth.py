import mail
from flask import Blueprint, render_template, request, redirect, url_for, flash
from web.models import User
from . import db
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from flask_mail import Message
from flask_login import current_user
from flask_login import login_required, current_user
from flask_login import login_user, logout_user, login_required

auth = Blueprint('auth', __name__)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('user')
        password = request.form.get('password')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email is taken", category="error")
            return render_template("signup.html")

        strong, message = User().check_strongpassword(password)
        if not strong:
            flash(message, category="error")
            return render_template("signup.html")

        new_user = User(email=email, user=username)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('views.home'))
    return render_template("signup.html")


@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('views.home'))

        flash("Wrong credentials", category="error")

    return "Login page"


@auth.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":
        email = request.form.get("email")

        if not email:
            flash("Please enter your email.", "error")
            return redirect(url_for("auth.forgot_password"))

        user = User.query.filter_by(email=email).first()

        if user:
            token = user.generate_reset_token()
            reset_link = url_for(
                "auth.reset_password",
                token=token,
                _external=True
            )
            print("RESET TOKEN:", token)

            msg = Message(
                "Password Reset Request",
                recipients=[email]
            )
            msg.body = f"Click the link to reset your password:\n{reset_link}"
            mail.send(msg)

        flash("If this email exists, a reset link was sent.", "success")
        return redirect(url_for("auth.login"))

    return "forgot_password.html"

@auth.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not current_user.check_password(current_password):
            flash("Current password is incorrect.", "error")
            return redirect(url_for("auth.change_password"))

        if new_password != confirm_password:
            flash("New passwords do not match.", "error")
            return change_password

        strong, message = current_user.check_strongpassword(new_password)
        if not strong:
            flash(message, "error")
            return redirect(url_for("auth.change_password"))

        current_user.set_password(new_password)
        db.session.commit()

        flash("Password changed successfully.", "success")
        return redirect(url_for("views.home"))

    return change_password.html


def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(auth.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(auth.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
        return email
    except Exception as e:
        return None

