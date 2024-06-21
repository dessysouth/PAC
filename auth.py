from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
import os
import yagmail
from db import db 
from model import * 
from forms import *

auth = Blueprint(
    'auth', __name__,
    template_folder='templates',
    static_folder='static'
)

# Initialize bcrypt
bcrypt = Bcrypt()

# Helper function to send reset email
# def send_reset_email(user):
#     token = user.get_reset_token()
#     reset_url = url_for('auth.reset_password', token=token, _external=True)
#     subject = "Password Reset Request"
#     body = f"""\
#     To reset your password, visit the following link:
#     {reset_url}
#     If you did not make this request then simply ignore this email.
#     """
#     yag = yagmail.SMTP(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
#     yag.send(to=user.email, subject=subject, contents=body)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            flash('Logged in successfully!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('student.student_dashboard'))
        else:
            flash('Login unsuccessful. Check email and password.', category='error')
    return render_template('login.html')

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category='success')
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']

        if password1 != password2:
            flash('Passwords do not match!', category='error')
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password1, method='pbkdf2:sha256')

        new_user = User(email=email, username=username, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)

            flash('Registration successful!', category='success')
            return redirect(url_for('home'))
        except IntegrityError:
            db.session.rollback()
            flash('Email address already in use.', category='error')
            return redirect(url_for('auth.register'))

    return render_template('register.html')

# @auth.route('/reset_password', methods=['GET', 'POST'])
# def reset_request():
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     form = RequestResetForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user:
#             send_reset_email(user)
#         flash('If an account with that email exists, a reset link has been sent.', 'info')
#         return redirect(url_for('auth.login'))
#     return render_template('reset_request.html', title='Reset Password', form=form)

# @auth.route('/reset_password/<token>', methods=['GET', 'POST'])
# def reset_password(token):
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     user = User.verify_reset_token(token)
#     if user is None:
#         flash('That is an invalid or expired token', 'warning')
#         return redirect(url_for('auth.reset_request'))
#     form = ResetPasswordForm()
#     if form.validate_on_submit():
#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#         user.password = hashed_password
#         db.session.commit()
#         flash('Your password has been updated! You are now able to log in', 'success')
#         return redirect(url_for('auth.login'))
#     return render_template('reset_password.html', title='Reset Password', form=form)
