from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField, PasswordField
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
from wtforms.validators import Email, DataRequired, URL, EqualTo


class RestaurantForm(FlaskForm):
    restaurant_name = StringField('Restaurant Name', validators=[DataRequired()])
    restaurant_url = StringField('Restaurant Website', validators=[
        DataRequired(), URL(require_tld=True, message="Invalid URL. Please enter a valid URL.")])
    email = StringField('Email', validators=[DataRequired(), Email()])
    menu = FileField('Upload Menu', validators=[DataRequired()])
    #script = FileField('Upload Script', validators=[DataRequired()])
    #other_instructions = StringField('Other Instructions (Optional)')
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')

class ConfirmationForm(FlaskForm):
    confirmation_code = StringField('Confirmation Code', validators=[DataRequired()])
    submit = SubmitField('Verify Code')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')