from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField, PasswordField, SelectField, ValidationError, IntegerField, RadioField
from wtforms.validators import Email, DataRequired, URL, EqualTo, Length, Optional

def OptionalURL(message=None):
    def _optional_url(form, field):
        if field.data and not URL(require_tld=True, message=message)(form, field):
            raise ValidationError(message or "Invalid URL. Please enter a valid URL.")
    return _optional_url


class RestaurantForm(FlaskForm):
    restaurant_name = StringField('Restaurant Name', validators=[DataRequired()])
    restaurant_url = StringField('Restaurant Website', validators=[
        URL()])
    #restaurant_url = StringField('Restaurant Website', validators=[
        #DataRequired(), URL(require_tld=True, message="Invalid URL. Please enter a valid URL.")])
    email = StringField('Email', validators=[DataRequired(), Email()])
    menu = FileField('Upload Menu')#, validators=[DataRequired()])
    currency = RadioField('Currency of your restaurant', choices=[('USD', 'US Dollar'), ('EUR', 'Euro')], validators=[DataRequired()])
    #script = FileField('Upload Script', validators=[DataRequired()])
    #other_instructions = StringField('Other Instructions (Optional)')
    
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')

def validate_seven_digit_number(form, field):
    if len(str(field.data)) < 7:
        raise ValidationError('The number must be at least 7 digits long.')

class RestaurantFormUpdate(FlaskForm):
    name = StringField('Restaurant Name', validators=[Optional()])
    website_url = StringField('Restaurant Website', validators=[Optional(),
        URL()])
    Add_MOM_AI_bot_chat = IntegerField('MOM AI Bot ID', validators=[Optional(), validate_seven_digit_number])

class UpdateMenuForm(FlaskForm):   
    menu_update = FileField('Upload New Menu', validators=[DataRequired()])
    submit = SubmitField('Update Menu')
    

class ConfirmationForm(FlaskForm):
    confirmation_code = StringField('Confirmation Code', validators=[DataRequired()])
    submit = SubmitField('Verify Code')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')