from model import *
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, login_user, logout_user, current_user, LoginManager
from flask_admin import Admin
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from paystack import initiate_payment 
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from db import db, app
from functools import wraps
from forms import StudentProfileForm, InstructorProfileForm
import os

app.config['SECRET_KEY'] = 'dnlmc/m;nclnsajx'

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

load_dotenv()
sk = os.environ.get('PAYSTACK_SECRET_KEY')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def instructor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'instructor':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'student':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    course_id = request.args.get('course_id')
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        if 'amount' in request.form:
            email = current_user.email
            amount = request.form['amount']

            auth_url, reference = initiate_payment(email, amount)

            if auth_url:
                return redirect(auth_url)
            else:
                flash('Error initiating payment.', category='error')
                return redirect(url_for('home'))
        else:
            return jsonify({'error': 'Amount not provided in the form data.'}), 400
    else:
        return render_template('payment.html', course=course)

@app.route('/')
@login_required
def home():
    if current_user.role == 'instructor':
        return redirect(url_for('instructor_home'))
    elif current_user.role == 'student':
        return redirect(url_for('home'))
    elif current_user.role == 'admin':
        return redirect(url_for('admin'))
    else:
        courses = Course.query.all()
        return render_template('index.html', courses=courses)



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

@app.route('/course/<int:course_id>/enroll')
@login_required
def enroll(course_id):
    course = Course.query.get_or_404(course_id)
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    if not student:
        flash('Please create a student profile to enroll in a course.', 'info')
        return redirect(url_for('create_student_profile', next=url_for('enroll', course_id=course_id)))

    return redirect(url_for('payment', course_id=course_id))



@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/add_course', methods=['GET', 'POST'])
@login_required
@admin_required
def add_course():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        duration = request.form['duration']
        image = request.files['image']

        if image:
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(app.static_folder, 'images', image_filename)
            if not os.path.exists(os.path.dirname(image_path)):
                os.makedirs(os.path.dirname(image_path))
            image.save(image_path)

            new_course = Course(
                title=title,
                description=description,
                price=price,
                category=category,
                duration=duration,
                image=image_filename,
                instructor_id=current_user.id  
            )

            try:
                db.session.add(new_course)
                db.session.commit()
                flash('Course added successfully!', category='success')
                return redirect(url_for('courses'))
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred: {e}', category='error')

    return render_template('add_course.html')


@app.route('/edit_course/<int:course_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    if request.method == 'POST':
        course.title = request.form['title']
        course.description = request.form['description']
        course.price = request.form['price']
        course.category = request.form['category']
        course.duration = request.form['duration']
        image = request.files['image']

        if image:
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(app.static_folder, 'images', image_filename)
            if not os.path.exists(os.path.dirname(image_path)):
                os.makedirs(os.path.dirname(image_path))
            image.save(image_path)
            course.image = image_filename

        try:
            db.session.commit()
            flash('Course updated successfully!', category='success')
            return redirect(url_for('courses'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', category='error')

    return render_template('edit_course.html', course=course)

@app.route('/delete_course/<int:course_id>', methods=['POST'])
@login_required
@admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    try:
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully!', category='success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {e}', category='error')

    return redirect(url_for('courses'))

@app.route('/admin', methods=['GET'])
@login_required
@admin_required
def admin():
    courses = Course.query.all()
    instructors = Instructor.query.all()
    students = Student.query.all()
    return render_template('admin.html', courses=courses, instructors=instructors, students=students)



@app.route('/instructor/dashboard', methods=['GET'], endpoint='instructor_alt')
@login_required
def instructor_dashboard_alt():
    if current_user.is_instructor():
        instructor_courses = Course.query.filter_by(instructor_id=current_user.id).all()
        return render_template('instructor.html', courses=instructor_courses)
    else:
        return redirect(url_for('instructor_home'))

@app.route('/instructor_home')
@login_required
def instructor_home():
    if current_user.is_instructor():
        return render_template('instructor.html')
    else:
        flash('You are not an instructor.', 'error')
        return redirect(url_for('home'))

@app.route('/create_student_profile', methods=['GET', 'POST'])
@login_required
def create_student_profile():
    form = StudentProfileForm()
    next_url = request.args.get('next')
    
    if form.validate_on_submit():
        profile_image = form.profile_image.data
        image_filename = secure_filename(profile_image.filename)
        image_directory = os.path.join(app.static_folder, 'profile_images')
        
        if not os.path.exists(image_directory):
            os.makedirs(image_directory)
        
        image_path = os.path.join(image_directory, image_filename)
        profile_image.save(image_path)
        
        student = Student(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            middlename=form.middlename.data,
            phone_number=form.phone_number.data,
            house_address=form.house_address.data,
            profile_image=image_filename,
            user_id=current_user.id
        )
        
        db.session.add(student)
        db.session.commit()
        flash('Student profile created successfully!', 'success')
        
        if next_url:
            return redirect(next_url)
        return redirect(url_for('home'))
    
    return render_template('create_student_profile.html', form=form)

# delete student profile
@app.route('/delete_student/<int:student_id>', methods=['POST'])
@login_required
@admin_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student has been deleted successfully.', 'success')
    return redirect(url_for('admin'))

# edit student profile
@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    form = StudentProfileForm(obj=student)
    if form.validate_on_submit():
        form.populate_obj(student)
        db.session.commit()
        flash('Student has been updated successfully.', 'success')
        return redirect(url_for('admin'))
    return render_template('edit_student.html', form=form, student=student)


@app.route('/create_instructor_profile', methods=['GET', 'POST'])
@login_required
def create_instructor_profile():
    form = InstructorProfileForm()
    if form.validate_on_submit():
        profile_image = form.profile_image.data
        image_filename = secure_filename(profile_image.filename)
        image_directory = os.path.join(app.static_folder, 'profile_images')
        
        if not os.path.exists(image_directory):
            os.makedirs(image_directory)
        
        image_path = os.path.join(image_directory, image_filename)
        profile_image.save(image_path)
        
        instructor = Instructor(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            phone_number=form.phone_number.data,
            house_address=form.house_address.data,
            profile_image=image_filename,
            user_id=current_user.id
        )
        
        try:
            db.session.add(instructor)
            db.session.commit()
            flash('Instructor profile created successfully!', 'success')
            return redirect(url_for('instructor_dashboard'))
        except IntegrityError:
            db.session.rollback()
            flash('Error creating instructor profile.', 'error')
            return redirect(url_for('create_instructor_profile'))

    return render_template('create_instructor_profile.html', form=form)

@app.route('/instructor/<int:instructor_id>')
@login_required
@admin_required
def view_instructor(instructor_id):
    instructor = Instructor.query.get_or_404(instructor_id)
    return render_template('view_instructor.html', instructor=instructor)


@app.route('/profile')
@login_required
def profile():
    if current_user.role == 'student':
        student = Student.query.filter_by(user_id=current_user.id).first()
        return render_template('profile.html', student=student)
    elif current_user.role == 'instructor':
        instructor = Instructor.query.filter_by(user_id=current_user.id).first()
        return render_template('profile.html', instructor=instructor)
    return render_template('profile.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            flash('Logged in successfully!', category='success')
            login_user(user, remember=True)
            if user.role == 'admin':
                return redirect(url_for('admin'))
            elif user.role == 'instructor':
                return redirect(url_for('instructor_alt'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Check email and password.', category='error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']
        role = request.form['role']

        if password1 != password2:
            flash('Passwords do not match!', category='error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password1, method='pbkdf2:sha256')

        new_user = User(email=email, username=username, password=hashed_password, role=role)

        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)

            flash('Registration successful!', category='success')

            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'instructor':
                return redirect(url_for('create_instructor_profile'))
            else:
                return redirect(url_for('create_student_profile'))
        except IntegrityError:
            db.session.rollback()
            flash('Email address already in use.', category='error')
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category='success')
    return redirect(url_for('login'))


@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    return 'Welcome Admin!'

@app.route('/instructor/dashboard')
@login_required
@instructor_required
def instructor_dashboard():
    return 'Welcome Instructor!'

@app.route('/student/dashboard')
@login_required
@student_required
def student_dashboard():
    return 'Welcome Student!'

if __name__ == '__main__':
    app.run(debug=True)
