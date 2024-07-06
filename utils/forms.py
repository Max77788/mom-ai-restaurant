from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, FileField, SubmitField, PasswordField, SelectField, ValidationError, IntegerField, RadioField
from wtforms.validators import Email, DataRequired, URL, EqualTo, Length, Optional

def OptionalURL(message=None):
    def _optional_url(form, field):
        if field.data and not URL(require_tld=True, message=message)(form, field):
            raise ValidationError(message or "Invalid URL. Please enter a valid URL.")
    return _optional_url


class RestaurantForm(FlaskForm):
    restaurant_name = StringField('Restaurant Name', validators=[DataRequired()])
    restaurant_url = StringField('Restaurant Website', validators=[Optional(),
        URL()])
    #restaurant_url = StringField('Restaurant Website', validators=[
        #DataRequired(), URL(require_tld=True, message="Invalid URL. Please enter a valid URL.")])
    email = StringField('Email', validators=[DataRequired(), Email()])
    menu = FileField('Upload Menu')#, validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    locationName = StringField('Location Name', validators=[DataRequired()])
    #currency = RadioField('Currency of your restaurant', choices=[('USD','USD'), ('EUR','EUR')], validators=[DataRequired()])
    #script = FileField('Upload Script', validators=[DataRequired()])
    #other_instructions = StringField('Other Instructions (Optional)')
    
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=20)])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match.')])
    
    # Add the field for image upload
    image = FileField('Upload Image', validators=[
        FileAllowed(['jpg', 'png'], 'Only images of .jpg and .png format')  # Restricting the file types to images only
    ])
    submit = SubmitField('Register')

def validate_seven_digit_number(form, field):
    if len(str(field.data)) < 7:
        raise ValidationError('The number must be at least 7 digits long.')

def validate_paypal_string(form, field):
    value = field.data
    # Check if the string is long and contains exactly three underscores in the middle
    if not value or len(value) < 10 or '___' not in value or value.find('___') not in range(1, len(value) - 3):
        raise ValidationError('Invalid PayPal secret and ID. It must be a long string with exactly three underscores in the middle.')

# Custom validator to check if description is at least 40 characters long
def validate_description_length(form, field):
    if field.data and len(field.data) < 40:
        raise ValidationError('Description must be at least 40 characters long.')



class RestaurantFormUpdate(FlaskForm):
    name = StringField('Restaurant Name', validators=[Optional()])
    website_url = StringField('Restaurant Website', validators=[Optional(),
        URL()])
    notif_destin = IntegerField('MOM AI Bot ID', validators=[Optional(), validate_seven_digit_number])
    image = FileField('Upload Image', validators=[
        Optional(), FileAllowed(['jpg', 'png'], 'Images only!')  # Restricting the file types to images only
    ])
    description = StringField('Restaurant Description', validators=[Optional(), validate_description_length])
    submit = SubmitField('Update')
    # pp_account = StringField('PayPal secret and ID', validators=[Optional(), validate_paypal_string])

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