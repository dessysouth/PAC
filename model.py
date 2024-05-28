from flask_login import UserMixin
from db import db, app
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    student_profile = db.relationship('Student', backref='user', uselist=False)
    instructor = db.relationship('Instructor', backref='user', uselist=False)
    

    def is_admin(self):
        return self.role == 'admin'

    def is_instructor(self):
        return self.role == 'instructor'
    


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(150))
    lastname = db.Column(db.String(150))
    middlename = db.Column(db.String(150))
    phone_number = db.Column(db.String(20))  
    house_address = db.Column(db.String(200))
    profile_image = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    courses = db.relationship('Course', backref='student', lazy=True)
    payments = db.relationship('Payment', backref='student', lazy=True)

class Instructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    middlename = db.Column(db.String(50), nullable=True)
    phone_number = db.Column(db.String(20), nullable=False)
    house_address = db.Column(db.String(100), nullable=True)
    profile_image = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

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
    payments = db.relationship('Payment', backref='course', lazy=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    reference = db.Column(db.String(10))
    email = db.Column(db.String(150))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    status = db.Column(db.String(10))

with app.app_context():
    db.create_all()
