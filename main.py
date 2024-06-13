from flask import Flask, render_template, request, flash, redirect, url_for,send_from_directory, abort
from flask_login import current_user, LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
from flask_mail import Mail, Message
from dotenv import load_dotenv
import smtplib
import logging
from auth import auth
from admin import admin
from student import student
from db import db, app
from model import *
from forms import *

# Configuration
app.config['SECRET_KEY'] = 'dnlmc/m;nclnsajx'
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
load_dotenv()
sk = os.environ.get('PAYSTACK_SECRET_KEY')

UPLOAD_FOLDER = os.path.join(app.static_folder, 'course_materials')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = os.getenv("MAIL_PORT")
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS")
MAIL_USE_SSL = os.getenv("MAIL_USE_SSL")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
SECRET_KEY = os.getenv("SECRET_KEY")

mail = Mail(app)

def send_email(msg):
    try:
        with mail.connect() as conn:
            conn.send(msg)
        return True
    except smtplib.SMTPServerDisconnected:
        print("SMTPServerDisconnected: Connection to the server was lost.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Routes
@app.route('/')
def home():
    courses = Course.query.all()
    print(f"Courses fetched: {courses}") 
    
    if current_user == 'student':
        student = Student.query.filter_by(user_id=current_user.id).first()
        if student:
            return render_template('index.html', student=student, courses=courses)
        else:
            flash('Please create a student profile.', 'info')
            return redirect(url_for('create_student_profile'))
   
    return render_template('index.html')




@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/courses')
def courses():
    all_courses = Course.query.all()
    return render_template('courses.html', courses=all_courses)

@app.route('/course/<int:course_id>')
def course(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course-single.html', course=course)

@app.route('/download_material/<int:material_id>')
def download_material(material_id):
    material = CourseMaterial.query.get_or_404(material_id)
    try:
        return send_from_directory(UPLOAD_FOLDER, material.filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route('/open_material/<int:material_id>')
def open_material(material_id):
    material = CourseMaterial.query.get_or_404(material_id)
    try:
        return send_from_directory(UPLOAD_FOLDER, material.filename, as_attachment=False)
    except FileNotFoundError:
        abort(404)



@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['eaddress']
        tel = request.form['tel']
        message = request.form['message']
        # Compose the email
        msg = Message('New Contact Form Submission',
                      recipients=['jacobbolarin@gmail.com'])
        msg.body = f"""
        From: {fname} {lname} <{email}>
        Phone: {tel}
        Message: {message}
        """
        # Send the email
        if send_email(msg):
            flash('Your message has been sent successfully!', 'success')
        else:
            flash('Failed to send your message. Please try again later.', 'danger')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(student)

if __name__ == '__main__':
    app.run(debug=True)