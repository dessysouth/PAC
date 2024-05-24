from flask_login import UserMixin
from db import db, app

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(150))
    lastname = db.Column(db.String(150))
    middlename = db.Column(db.String(150))
    phone_number = db.Column(db.Integer())
    house_address = db.Column(db.String(200))
    user = db.Column(db.ForeignKey('user.id'))
    
class Instructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(150))
    lastname = db.Column(db.String(150))
    middlename = db.Column(db.String(150))
    phone_number = db.Column(db.Integer())
    user = db.Column(db.ForeignKey('user.id'))
    course = db.Column(db.ForeignKey('course.id'))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    description = db.Column(db.String(500))
    price = db.Column(db.Float)
    student = db.Column(db.ForeignKey('student.id'))
    payment = db.relationship('Payment', backref='course', lazy=True)
    duration = db.Column(db.String(30))
    instructor = db.Column(db.ForeignKey('instructor.id'))




class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    reference = db.Column(db.String(10))
    email = db.Column(db.String(150))
    student = db.Column(db.ForeignKey('student.id'))
    status = db.Column(db.String(10))

   
with app.app_context():
   db.create_all()