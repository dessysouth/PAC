from datetime import datetime
from flask_login import UserMixin
from db import db, app
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    cart_items = db.relationship('Cart', back_populates='user')
    student_profile = db.relationship('Student', back_populates='user', uselist=False)


    def __repr__(self):
        return f'<User {self.username}>'


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(150))
    lastname = db.Column(db.String(150))
    middlename = db.Column(db.String(150))
    phone_number = db.Column(db.String(20))
    house_address = db.Column(db.String(200))
    profile_image = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='student_profile')
    courses = db.relationship('Course', backref='student', lazy=True)
    payments = db.relationship('Payment', back_populates='student')

class Instructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(150))
    email = db.Column(db.String(150))
    phone_number = db.Column(db.String(20))
    house_address = db.Column(db.String(200))
    profile_image = db.Column(db.String(150))
    courses = db.relationship('Course', back_populates='instructor')

    def __repr__(self):
        return f'<Instructor {self.fullname}>'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    description = db.Column(db.String(500))
    price = db.Column(db.Float)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'))
    image = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(30))
    instructor = db.relationship('Instructor', back_populates='courses')
    payments = db.relationship('Payment', back_populates='course')


    def __repr__(self):
        return f'<Course {self.title}>'

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', back_populates='cart_items')
    course = db.relationship('Course')

    def __repr__(self):
        return f'<Cart {self.id}>'

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    reference = db.Column(db.String(50))
    email = db.Column(db.String(150))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    status = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='payments')

    student = db.relationship('Student', back_populates='payments')
    course = db.relationship('Course', back_populates='payments')


class CourseMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    filename = db.Column(db.String(150), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    course = db.relationship('Course', back_populates='materials')

Course.materials = db.relationship('CourseMaterial', back_populates='course', cascade='all, delete-orphan')




with app.app_context():
    db.create_all()
