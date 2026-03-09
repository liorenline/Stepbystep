import sqlalchemy as sa
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.sql.functions import current_user
from .models import User
from . import db
from flask import render_template
from app import app
from .forms import LoginForm
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, login_required


@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        user = request.form.get('user')
        email = request.form.get('email')
        password = request.form.get('password')

        new_user = User(email=email,password=generate_password_hash(password), user = user)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('views.home'))
    return render_template("signup.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@app.route('/user/<user>')
def show_user_profile(user):
  return render_template("acc.html")