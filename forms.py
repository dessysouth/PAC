from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, EqualTo

class CourseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    duration = StringField('Duration', validators=[DataRequired()])
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

class InstructorProfileForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    house_address = StringField('House Address', validators=[DataRequired()])
    profile_image = FileField('Profile Image')
    submit = SubmitField('Create Profile')

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
