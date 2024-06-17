from pypstk import payment
from flask import Blueprint, request, redirect, url_for, render_template, flash
from model import *
import os 
from dotenv import load_dotenv
from flask_login import login_required, login_user, logout_user, current_user, LoginManager

load_dotenv()
sk= os.environ.get('secret_key')
app.config['secret_key'] = os.environ.get('secret_key')
pay =  Blueprint(
    'pay', __name__,
    template_folder='templates',
    static_folder='static'
  )

@pay.route('/success', methods=['GET'])
@login_required
def success_page():
    return render_template('success.html')

@pay.route('/payment/<int:course_id>', methods=['GET', 'POST'])
@login_required
def payment(course_id):
    course = Course.query.get_or_404(course_id) 
    user = current_user 

    if request.method == 'POST':
        email = request.form['email']
        amount = request.form['amount']
        proc = Payment(email=email, amount=amount, sk=sk)
        data = proc.initialize_transaction()
        auth_url = data['auth_url']
        ref = data['reference']
        return auth_url
        
        flash('Payment successful!', 'success') 
        return redirect(url_for('success_page'))

    user_email = user.email
    course_price = course.price
    return render_template('payment.html', user_email=user_email, course_price=course_price, course=course)