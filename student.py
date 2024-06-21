from flask import Blueprint
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, abort, g
from flask_login import login_required, login_user, logout_user, current_user, LoginManager
import os
import logging
from pypstk.payment import Payment
from db import db, app
from model import *
from forms import *
import requests

student = Blueprint(
    'student', __name__,
    template_folder='templates',
    static_folder='static'
  )

app.config['secret_key'] = os.environ.get('secret_key')

secret_key = app.config['secret_key']
PAYSTACK_BASE_URL = "https://api.paystack.co"

app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/uploads')
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@student.route('/student/dashboard')
def student_dashboard():
    return redirect(url_for('home'))

@student.route('/profile')
@login_required
def profile():
    if current_user.role == 'student':
        student = Student.query.filter_by(user_id=current_user.id).first()
        return render_template('profile.html', user=current_user, student=student)
    elif current_user.role == 'instructor':
        instructor = Instructor.query.filter_by(user_id=current_user.id).first()
        return render_template('profile.html', user=current_user, instructor=instructor)
    return render_template('profile.html', user=current_user)

@student.route('/create_student_profile', methods=['GET', 'POST'])
@login_required
def create_student_profile():
    form = StudentProfileForm()
    next_page = request.args.get('next')
    if form.validate_on_submit():
        # Process form data
        firstname = form.firstname.data
        lastname = form.lastname.data
        middlename = form.middlename.data
        phone_number = form.phone_number.data
        house_address = form.house_address.data
        profile_image = form.profile_image.data

        # Save the student profile
        student = Student(
            user_id=current_user.id,
            firstname=firstname,
            lastname=lastname,
            middlename=middlename,
            phone_number=phone_number,
            house_address=house_address,
            profile_image=profile_image.filename if profile_image else None
        )
        db.session.add(student)
        db.session.commit()

        # Save profile image if provided
        if profile_image:
            profile_image.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_image.filename))

        flash('Student profile created successfully.', 'success')
        return redirect(next_page or url_for('index'))
    return render_template('create_student_profile.html', form=form, next=next_page)


@student.route('/course/<int:course_id>/enroll')
@login_required
def enroll(course_id):
    course = Course.query.get_or_404(course_id)
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash('Please create a student profile to enroll in a course.', 'info')
        return redirect(url_for('student.create_student_profile', next=url_for('student.enroll', course_id=course_id)))
    return redirect(url_for('student.payment', course_id=course_id))


@student.context_processor
def inject_cart_data():
    cart_count = 0
    cart_items = []
    if current_user.is_authenticated:
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        cart_count = len(cart_items)
    return dict(cart_count=cart_count, cart_items=cart_items)

@student.before_request
def before_request():
    if current_user.is_authenticated:
        g.cart_count = Cart.query.filter_by(user_id=current_user.id).count()
        g.cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    else:
        g.cart_count = 0
        g.cart_items = []

@student.route('/debug')
def debug():
    if current_user.is_authenticated:
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        cart_count = len(cart_items)
        return f"User: {current_user.username}, Cart Count: {cart_count}, Cart Items: {[item.course.title for item in cart_items]}"
    else:
        return "User not authenticated"

@student.route('/add_to_cart/<int:course_id>', methods=['POST'])
@login_required
def add_to_cart(course_id):
    course = Course.query.get_or_404(course_id)
    if Cart.query.filter_by(user_id=current_user.id, course_id=course_id).first():
        flash('This course is already in your cart.', 'info')
    else:
        cart_item = Cart(user_id=current_user.id, course_id=course_id)
        db.session.add(cart_item)
        db.session.commit()
        flash('Course added to cart.', 'success')
    return redirect(url_for('student.view_cart'))

@student.route('/view_cart')
@login_required
def view_cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    return render_template('view_cart.html', cart_items=cart_items)

@student.route('/cart/remove_from_cart/<int:cart_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    db.session.delete(cart_item)
    db.session.commit()
    flash('Course removed from cart.', 'success')
    return redirect(url_for('student.view_cart'))

def initialize_payment(email, amount):
    try:
        amount_in_kobo = int(float(amount) * 100)  # Convert to kobo
    except ValueError:
        raise ValueError("Invalid amount format")

    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json",
    }
    data = {
        "email": email,
        "amount": amount_in_kobo,
    }
    response = requests.post(f"{PAYSTACK_BASE_URL}/transaction/initialize", headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        print("Payment initialized:", response_data)
        return response_data['data']['authorization_url'], response_data['data']['reference']
    else:
        print("Error initializing payment:", response.text)
        return None, None

@student.route('/course/<int:course_id>/payment', methods=['GET', 'POST'])
@login_required
def payment(course_id):
    course = Course.query.get_or_404(course_id)
    if request.method == 'POST':
        email = request.form.get('email')
        amount = request.form.get('amount')

        # Ensure the amount is correctly formatted
        try:
            amount = float(amount)
        except ValueError:
            flash('Invalid amount format.', 'danger')
            return redirect(url_for('student.payment', course_id=course.id))

        auth_url, reference = initialize_payment(email, amount)

        if auth_url:
            # Fetch the student profile associated with the current user
            student_profile = Student.query.filter_by(user_id=current_user.id).first()

            if not student_profile:
                flash('Student profile not found.', 'danger')
                return redirect(url_for('student.payment', course_id=course.id))

            # Save the payment details to the database
            payment = Payment(
                amount=amount,
                reference=reference,
                email=email,
                course_id=course.id,
                user_id=current_user.id,
                student_id=student_profile.id,
                status='success'
            )
            db.session.add(payment)
            db.session.commit()
            return redirect(auth_url)
        else:
            flash('An error occurred while initializing payment.', 'danger')
            return redirect(url_for('student.payment', course_id=course.id))
    return render_template('payment.html', course=course)

@student.route('/verify_payment/<reference>')
def verify_payment(reference):
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json",
    }
    response = requests.get(f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}", headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        print("Verification response:", response_data)
        if response_data['data']['status'] == 'success':
            payment = Payment.query.filter_by(reference=reference).first()
            if payment:
                payment.status = 'successful'
                db.session.commit()

                # Remove the course from the cart
                cart_item = Cart.query.filter_by(user_id=payment.user_id, course_id=payment.course_id).first()
                if cart_item:
                    db.session.delete(cart_item)
                    db.session.commit()

                flash('Payment successful!', 'success')
                return redirect(url_for('student.course', course_id=payment.course_id))
            else:
                print("Payment not found in the database.")
                flash('Payment not found in the database.', 'danger')
                return redirect(url_for('student.courses'))
    else:
        print("Payment verification failed:", response.text)
        flash('Payment verification failed.', 'danger')
        return redirect(url_for('student.courses'))