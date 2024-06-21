from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, SubmitField, FileField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Length, Email, EqualTo
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, FileField
from wtforms.validators import InputRequired, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField
from model import *

# class RequestResetForm(FlaskForm):
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     submit = SubmitField('Request Password Reset')

# class ResetPasswordForm(FlaskForm):
#     password = PasswordField('Password', validators=[DataRequired()])
#     confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
#     submit = SubmitField('Reset Password')


class CourseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    duration = StringField('Duration', validators=[DataRequired()])
    instructor = StringField('Name of Instructor', validators=[DataRequired()])  # Add this line
    image = FileField('Course Image')
    submit = SubmitField('Save Changes')

class StudentProfileForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    middlename = StringField('Middle Name')
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    house_address = StringField('House Address', validators=[DataRequired()])
    profile_image = FileField('Profile Image')
    submit = SubmitField('Save Changes')

class EditStudentForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    middlename = StringField('Middle Name')
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    house_address = StringField('House Address', validators=[DataRequired()])
    profile_image = FileField('Profile Image')
    submit = SubmitField('Update Profile')
    

class CreateInstructorForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    fullname = StringField('Full Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    house_address = StringField('House Address', validators=[DataRequired()])
    profile_image = FileField('Profile Image', validators=[DataRequired()])
    submit = SubmitField('Create Instructor')



class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password1 = StringField('Password', validators=[DataRequired()])
    password2 = StringField('Confirm Password', validators=[DataRequired(), EqualTo('password1')])
    role = StringField('Role', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EditCourseForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    description = TextAreaField('Description', validators=[InputRequired()])
    price = DecimalField('Price', validators=[InputRequired(), NumberRange(min=0)])
    category = StringField('Category', validators=[InputRequired()])
    duration = StringField('Duration', validators=[InputRequired()])
    instructor = QuerySelectField('Instructor', query_factory=lambda: Instructor.query.all(), get_label='fullname')
    image = FileField('Course Image')

class EditInstructorForm(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    house_address = StringField('House Address', validators=[DataRequired()])
    profile_image = FileField('Profile Image')
    submit = SubmitField('Update Profile')

class CourseMaterialForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    file = FileField('File', validators=[DataRequired()])
    submit = SubmitField('Upload')

