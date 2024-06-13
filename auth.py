from flask import Blueprint
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, login_user, logout_user, current_user, LoginManager
from sqlalchemy.exc import IntegrityError
import os
from db import db, app
from model import *
from forms import *

auth = Blueprint(
    'auth', __name__,
    template_folder='templates',
    static_folder='static'
  )
UPLOAD_FOLDER = 'static/uploads/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/uploads')
# if not os.path.exists(app.config['UPLOAD_FOLDER']):
#     os.makedirs(app.config['UPLOAD_FOLDER'])


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


