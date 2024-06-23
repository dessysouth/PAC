from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, abort, g, session
from flask_login import current_user, LoginManager, login_required
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
from dotenv import load_dotenv
import logging
from auth import auth
from admin import admin
from student import student
from db import db, app
from model import *
from forms import *
from flask_mail import Mail

# Configuration
app.config['SECRET_KEY'] = 'dnlmc/m;nclnsajx'
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
load_dotenv()
sk = os.environ.get('PAYSTACK_SECRET_KEY')


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration for course materials upload folder
COURSE_UPLOAD_FOLDER = os.path.join(app.static_folder, 'course_materials')
if not os.path.exists(COURSE_UPLOAD_FOLDER):
    os.makedirs(COURSE_UPLOAD_FOLDER)

# Configuration for general file uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuration for profile pictures upload folder
PROFILE_PICS_FOLDER = 'static/uploads/profile_pics'
if not os.path.exists(PROFILE_PICS_FOLDER):
    os.makedirs(PROFILE_PICS_FOLDER)

# Allowed extensions for profile pictures
PROFILE_PICS_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check if a filename has an allowed extension for general file uploads
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to check if a filename has an allowed extension for profile pictures
def allowed_profile_pic(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in PROFILE_PICS_EXTENSIONS

# User Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_cart_count():
    cart_count = 0
    if current_user.is_authenticated:
        cart_count = Cart.query.filter_by(user_id=current_user.id).count()
    return dict(cart_count=cart_count)

# Routes
@app.route('/')
def home():
    courses = Course.query.limit(3).all() 
    print(f"Courses fetched: {courses}") 
    
    if current_user == 'student':
        student = Student.query.filter_by(user_id=current_user.id).first()
        if student:
            return render_template('index.html', student=student, courses=courses)
        else:
            flash('Please create a student profile.', 'info')
            return redirect(url_for('create_student_profile'))
   
    return render_template('index.html', courses=courses)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/courses')
def courses():
    all_courses = Course.query.all()
    return render_template('courses.html', courses=all_courses)


@app.route('/course/<int:course_id>')
@login_required
def course(course_id):
    course = Course.query.get_or_404(course_id)
    payment_exists = False
    course_materials = []

    if current_user.is_authenticated:
        payment = Payment.query.filter_by(user_id=current_user.id, course_id=course_id, status='success').first()
        if payment:
            payment_exists = True
            course_materials = CourseMaterial.query.filter_by(course_id=course_id).all()

    return render_template('course-single.html', course=course, payment_exists=payment_exists, course_materials=course_materials)

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
    return render_template('contact.html')

@app.before_request
def before_request():
    if current_user.is_authenticated:
        g.cart_count = Cart.query.filter_by(user_id=current_user.id).count()
        g.cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    else:
        g.cart_count = 0
        g.cart_items = []


app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(student)

if __name__ == '__main__':
    app.run(debug=True)
