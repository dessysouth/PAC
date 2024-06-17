from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
import os
from sqlalchemy.exc import IntegrityError
import logging
from pypstk.payment import Payment
from db import db, app
from model import *
from forms import *

# Define the admin Blueprint
admin = Blueprint('admin', __name__, template_folder='templates/admin', static_folder='static')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set upload folder for course materials
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'course_materials')
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Set upload folder for profile pictures
PROFILE_PICS_FOLDER = 'static/uploads/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the profile pictures folder exists
if not os.path.exists(PROFILE_PICS_FOLDER):
    os.makedirs(PROFILE_PICS_FOLDER)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file, folder):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(folder, filename)
        file.save(filepath)
        return filename
    else:
        raise ValueError('File not allowed')


@admin.route('/admin', methods=['GET'])
def admin_dashboard():
    courses = Course.query.all()
    cart_items = Cart.query.all()
    payments = Payment.query.all()
    students = Student.query.all()
    instructors = Instructor.query.all()  # Fetch all instructors

    # Debugging print statements
    for instructor in instructors:
        print(f"Instructor: {instructor.fullname}, Image: {instructor.profile_image}")

    for student in students:
        print(f"Student: {student.firstname}, Image: {student.profile_image}")

    return render_template('admin.html', courses=courses, cart_items=cart_items, payments=payments,
                           instructors=instructors, students=students)

@admin.route('/delete_instructor/<int:instructor_id>', methods=['POST'])
# @login_required
def delete_instructor(instructor_id):
    instructor = Instructor.query.get_or_404(instructor_id)
    try:
        if instructor.profile_image:
            image_path = os.path.join(PROFILE_PICS_FOLDER, instructor.profile_image)
            if os.path.exists(image_path):
                os.remove(image_path)
        db.session.delete(instructor)
        db.session.commit()
        flash('Instructor deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting instructor: {e}', 'error')
    return redirect(url_for('admin.admin_dashboard'))

@admin.route('/delete_student/<int:student_id>', methods=['POST'])
# @login_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    try:
        if student.profile_image:
            image_path = os.path.join(PROFILE_PICS_FOLDER, student.profile_image)
            if os.path.exists(image_path):
                os.remove(image_path)
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting student: {e}', 'error')
    
    return redirect(url_for('admin.admin_dashboard'))

@admin.route('/create_instructor', methods=['GET', 'POST'])
def create_instructor():
    form = CreateInstructorForm()
    if form.validate_on_submit():
        profile_image = form.profile_image.data
        image_filename = secure_filename(profile_image.filename)
        image_path = os.path.join(PROFILE_PICS_FOLDER, image_filename)
        
        if allowed_file(image_filename):
            profile_image.save(image_path)

            instructor = Instructor(
                email=form.email.data,
                fullname=form.fullname.data,
                phone_number=form.phone_number.data,
                house_address=form.house_address.data,
                profile_image=image_filename, 
            )
            
            try:
                db.session.add(instructor)
                db.session.commit()
                flash('Instructor profile created successfully!', 'success')
                return redirect(url_for('admin.admin_dashboard'))
            except IntegrityError:
                db.session.rollback()
                flash('An error occurred. Please try again.', 'error')
        else:
            flash('Invalid file format. Please upload an image file.', 'error')

    return render_template('create_instructor_profile.html', form=form)

@admin.route('/edit_instructor/<int:instructor_id>', methods=['GET', 'POST'])
# @login_required
def edit_instructor(instructor_id):
    instructor = Instructor.query.get_or_404(instructor_id)
    form = EditInstructorForm(obj=instructor)
    if form.validate_on_submit():
        form.populate_obj(instructor)
        if form.profile_image.data:
            filename = secure_filename(form.profile_image.data.filename)
            filepath = os.path.join(PROFILE_PICS_FOLDER, filename)
            if allowed_file(filename):
                form.profile_image.data.save(filepath)
                instructor.profile_image = filename
            else:
                flash('Invalid file format. Please upload an image file.', 'error')
        db.session.commit()
        flash('Instructor profile updated successfully.', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('edit_instructor.html', form=form, instructor=instructor)

@admin.route('/add_course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        category = request.form.get('category')
        duration = request.form.get('duration')
        instructor_name = request.form.get('instructor')
        image = request.files.get('image')

        # Print the received form data for debugging
        print(f"Received form data: title={title}, description={description}, price={price}, category={category}, duration={duration}, instructor_name={instructor_name}, image={image}")

        if image:
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            if not os.path.exists(os.path.dirname(image_path)):
                os.makedirs(os.path.dirname(image_path))
            image.save(image_path)

            # Fetch the instructor by full name
            instructor = Instructor.query.filter_by(fullname=instructor_name).first()

            # Debugging print statements
            if instructor:
                print(f"Found instructor: {instructor.fullname}")
            else:
                print(f"Instructor {instructor_name} not found in the database.")

                # Optionally add the instructor if not found
                new_instructor = Instructor(fullname=instructor_name)
                db.session.add(new_instructor)
                db.session.commit()
                instructor = new_instructor
                print(f"Added new instructor: {instructor.fullname}")

            new_course = Course(
                title=title,
                description=description,
                price=price,
                category=category,
                duration=duration,
                image=image_filename,
                instructor_id=instructor.id  # Associate the course with the instructor
            )

            try:
                db.session.add(new_course)
                db.session.commit()
                flash('Course added successfully!', 'success')
                return redirect(url_for('admin.admin_dashboard'))
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred: {e}', 'danger')

    return render_template('add_course.html')

@admin.route('/upload_material/<int:course_id>', methods=['GET', 'POST'])
def upload_material(course_id):
    form = CourseMaterialForm()
    course = Course.query.get_or_404(course_id)

    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure unique filename
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        # Save the file
        file.save(filepath)

        new_material = CourseMaterial(
            course_id=course.id,
            filename=filename,
            filepath=filepath,
            description=form.description.data
        )

        try:
            db.session.add(new_material)
            db.session.commit()
            flash('Material uploaded successfully!', 'success')
            return redirect(url_for('admin.admin_dashboard'))  # Redirect to admin dashboard
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')

    return render_template('upload_material.html', form=form, course=course)

@admin.route('/edit_course/<int:course_id>', methods=['GET', 'POST'])
# @login_required  # Uncomment if login is required to edit courses
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    form = EditCourseForm(obj=course)

    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        price = form.price.data
        category = form.category.data
        duration = form.duration.data
        instructor_name = form.instructor.data.fullname  # Assuming instructor.data returns an Instructor instance
        image = form.image.data

        # Print the received form data for debugging
        print(f"Received form data: title={title}, description={description}, price={price}, category={category}, duration={duration}, instructor_name={instructor_name}, image={image}")

        if image:
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            if not os.path.exists(os.path.dirname(image_path)):
                os.makedirs(os.path.dirname(image_path))
            image.save(image_path)

            # Remove old image if it exists
            if course.image:
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], course.image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            course.image = image_filename

        # Fetch the instructor by full name
        instructor = Instructor.query.filter_by(fullname=instructor_name).first()

        # Debugging print statements
        if instructor:
            print(f"Found instructor: {instructor.fullname}")
        else:
            print(f"Instructor {instructor_name} not found in the database.")

            # Optionally add the instructor if not found
            new_instructor = Instructor(fullname=instructor_name)
            db.session.add(new_instructor)
            db.session.commit()
            instructor = new_instructor
            print(f"Added new instructor: {instructor.fullname}")

        # Update course details
        course.title = title
        course.description = description
        course.price = price
        course.category = category
        course.duration = duration
        course.instructor_id = instructor.id

        try:
            db.session.commit()
            flash('Course updated successfully!', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')

    return render_template('edit_course.html', form=form, course=course)




@admin.route('/delete_course/<int:course_id>', methods=['POST'])
# @login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    try:
        if course.image:
            image_path = os.path.join(admin.static_folder, 'course_images', course.image)
            if os.path.exists(image_path):
                os.remove(image_path)

        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {e}', 'error')

    return redirect(url_for('admin.admin_dashboard'))

@admin.route('/cart/remove/<int:cart_id>', methods=['POST'])
def admin_remove_from_cart(cart_id):
    if not current_user.is_authenticated or not isinstance(current_user._get_current_object()):
        abort(403)
    cart_item = Cart.query.get_or_404(cart_id)
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart.', 'success')
    return redirect(url_for('admin.admin_dashboard'))

@admin.route('/admin/payments')
def admin_payments():
    payments = Payment.query.filter_by(status='success').all()
    return render_template('admin/payments.html', payments=payments)

# @admin.route('/register_admin', methods=['GET'])
# def register_admin():
#     with app.app_context():
#         email = 'jacobbolarin@gmail.com'
#         password = 'funke1328'
#         hashed_password = generate_password_hash(password).encode('utf-8')
#         new_admin = Admin(email=email, password=hashed_password)
#         db.session.add(new_admin)
#         db.session.commit()
#         return 'Admin registered successfully!'

