from flask import Blueprint, request, flash, redirect, url_for
from . import db
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user

auth = Blueprint('auth', __name__)

@auth.route("/login", methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logeed in succesfully!', category = 'success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password', category='error')
        else:
            flash('Email does not exist', category = 'error')

    return "login"

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()

        has_upp = has_sp = has_num = False
        for c in password1:
            if c.isupper():
                has_upp = True
            elif c.isdigit():
                has_num = True
            elif not c.isalnum():
                has_sp = True

        if user:
            flash('Email already exists', category='error')
        elif len(email) < 4:
            flash('Email is too short', category='error')
        elif len(firstName) < 2:
            flash('Name is too short', category='error')
        elif len(password1) < 8:
            flash('Password is too short', category='error')
        elif not has_upp:
            flash('Password has no upper letters', category='error')
        elif not has_num:
            flash('Password has no numbers', category='error')
        elif not has_sp:
            flash('Password has no special characters', category='error')
        elif password1 != password2:
            flash('Passwords do not match', category='error')
        if not email or not firstName or not password1 or not password2:
            flash('All fields must be filled', category='error')
        else:
            new_user = User(email=email, first_name=firstName, password=generate_password_hash(password1))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return "sign-up"
