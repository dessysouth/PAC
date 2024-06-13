from flask import Blueprint
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, abort, g
from flask_login import login_required, login_user, logout_user, current_user, LoginManager
import os
import logging
from pypstk.payment import Payment
from db import db, app
from model import *
from forms import *

student = Blueprint(
    'student', __name__,
    template_folder='templates',
    static_folder='static'
  )

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


@student.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    course_id = request.args.get('course_id')
    course = Course.query.get_or_404(course_id)
    user = current_user
    
        
    if request.method == 'POST':
        if 'amount' in request.form:
            email = current_user.email
            amount = request.form['amount']


            pay = Payment(email=email, amount=amount, course_id=course_id, sk=sk)
            response = pay.initialize_transaction()
            auth_url = response['auth_url']
            print(auth_url)
            

            if auth_url:
                return auth_url
            else:
                flash('Error initiating payment.', category='error')
                return redirect(url_for('home'))
        else:
            return jsonify({'error': 'Amount not provided in the form data.'}), 400
    else:
        return render_template('payment.html', course=course)