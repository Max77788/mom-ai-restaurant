from flask import Flask, abort, make_response, jsonify, request, render_template, session, redirect, url_for, flash, render_template_string, Response, send_file
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from werkzeug.utils import secure_filename
import os
# from google.cloud import speech
import qrcode
import bcrypt
#from io import BytesIO
#from flask_socketio import SocketIO, disconnect
import gridfs
from pydub import AudioSegment
import uuid
import re
import base64
from bs4 import BeautifulSoup
import markdown
import json
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
#from pyrogram import filters
#from utils.telegram import app_tg
from utils.forms import ChangeCredentialsForm, RestaurantForm, UpdateMenuForm, ConfirmationForm, LoginForm, RestaurantFormUpdate 
from functions_to_use import send_email_raw, mint_and_send_tokens, convert_and_transcribe_audio_azure, convert_and_transcribe_audio_openai, send_confirmation_email_quick_registered, generate_random_string, generate_short_voice_output, app, get_post_filenames, get_post_content_and_headline, InvalidMenuFormatError, CONTRACT_ABI, generate_qr_code_and_upload, remove_formatted_lines, convert_hours_to_time, setup_working_hours, hash_password, check_password, clear_collection, upload_new_menu, convert_xlsx_to_txt_and_menu_html, create_assistant, insert_restaurant, get_assistants_response, send_confirmation_email, generate_code, check_credentials, send_telegram_notification, send_confirmation_email_request_withdrawal, send_waitlist_email, send_confirmation_email_registered, convert_webm_to_wav, MOM_AI_EXEMPLARY_MENU_HTML, MOM_AI_EXEMPLARY_MENU_FILE_ID, MOM_AI_EXEMPLARY_MENU_VECTOR_ID 
from pymongo import MongoClient
from flask_mail import Mail, Message
from utils.web3_functionality import create_web3_wallet, completion_on_binance_web3_wallet_withdraw
import base64
#from utils.hyperwallet import create_user, create_bank_account, make_payment
import ast
import markdown2
from utils.pp_payment import createPayment, executePayment, get_subscription_status, createOrder, captureOrder
#from utils.withdraw.pp_payout import send_payout_pp
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from openai import OpenAI, AzureOpenAI
from apscheduler.schedulers.background import BackgroundScheduler
from bson import ObjectId  # Import ObjectId from bson
import io
from web3 import Web3
from flask_httpauth import HTTPBasicAuth
import logging
import pytz
#from tools.stellar_payments.list_payments import list_received_payments
#from tools.stellar_payments.create_account import create_stellar_account
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import time

"""
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',)  # Append mode

# Configure APScheduler logging
scheduler_logger = logging.getLogger('apscheduler')
scheduler_logger.setLevel(logging.DEBUG)
scheduler_logger.addHandler(logging.StreamHandler())  # Also log to the console
"""

app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY")
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL_CORRECT', 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


# Define the Post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url_slug = db.Column(db.String(150), nullable=True, unique=True, index=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)



app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")

# DROP_THE_EXISTING_TABLES = os.environ.get("DROP_THE_EXISTING_TABLES", "False") == "True"

# print("Drop the existing tables = ", DROP_THE_EXISTING_TABLES)

# Ensure the tables are created
with app.app_context():
    #if DROP_THE_EXISTING_TABLES:
        #db.drop_all()
        #print("Dropped the tables")
    db.create_all()


CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID") if os.environ.get("PAYPAL_SANDBOX") == "True" else os.environ.get("PAYPAL_LIVE_CLIENT_ID")
SECRET_KEY = os.environ.get("PAYPAL_SECRET_KEY") if os.environ.get("PAYPAL_SANDBOX") == "True" else os.environ.get("PAYPAL_LIVE_SECRET_KEY")

auth = HTTPBasicAuth()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app.config.from_object(Config)


# Define users and passwords
users = {
    os.environ.get('BLOG_USERNAME'): generate_password_hash(os.environ.get('BLOG_PASSWORD'))
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username


# Initialize Flask-Mail
app.config['MAIL_SERVER'] = 'mail.privateemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'contact@mom-ai-agency.site'
app.config['MAIL_PASSWORD'] = os.environ.get("PRIVATEEMAIL_PASSWORD")
FROM_EMAIL = app.config['MAIL_USERNAME']
mail = Mail(app)



if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.mkdir(app.config['UPLOAD_FOLDER'])

mongodb_connection_string = os.environ.get("MONGODB_CONNECTION_URI")

# Connect to MongoDB
client_db = MongoClient(mongodb_connection_string)

# Specify the database name
db_mongo = client_db['MOM_AI_Restaurants']

# Specify the collection name
collection = db_mongo[os.environ.get("DB_VERSION")]

db_order_dashboard = client_db["Dashboard_Orders"]

db_rest_reviews = client_db["restaurant_reviews"]

db_items_cache = client_db["Items_Cache"]

CLIENT_OPENAI = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
"""
CLIENT_OPENAI = AzureOpenAI(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),  
    api_version="2024-02-15-preview",
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
)
"""

EXCHANGE_API_KEY = os.environ.get("EXCHANGE_API_KEY")
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
AZURE_SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID")

fs = gridfs.GridFS(db_mongo)

print("Everything Initialized!")

"""
@app.route('/redirect', methods=['GET', 'POST'])
def handle_redirect():
    print(f"Request on /redirect {request}")
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return redirect('/waitlist')
    else:
        abort(403)  # Forbidden
"""


clients = {}

@app.errorhandler(403)
def forbidden(e):
    return render_template("errors/403_error_template.html", title="Error 403"), 403

@app.errorhandler(404)
def error_404(e):
    return render_template("errors/404_error_template.html", title="Error 404"), 404


# Define error handler for 500 internal server error
@app.errorhandler(500)
def internal_server_error(error):
    # Log the error if necessary
    app.logger.error(f"Server Error: {error}")
    # Redirect to the main page
    flash("Internal Server Error Occurred - you were redirected to the main page")
    return redirect(url_for('landing_page'))


def schedule_tasks():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=clear_collection, trigger="interval", minutes=15)
    scheduler.add_job(func=setup_working_hours, trigger="interval", seconds=15)
    scheduler.start()
    print("The scheduler started")


with app.app_context():
    schedule_tasks()
    


# Middleware to modify headers
@app.after_request
def add_header(response):
    response.headers['X-Frame-Options'] = 'ALLOWALL'  # Allow all domains to embed
    return response

"""
########### SocketIO Stuff #############

@socketio.on('connect')
def handle_connect():
    clients[request.sid] = {}
    print('Client connected:', request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    client_id = request.sid
    if client_id in clients:
        if 'thread' in clients[client_id] and clients[client_id]['thread'].is_alive():
            clients[client_id]['cancel'] = True
        del clients[client_id]
    print('Client disconnected:', client_id)

########### SocketIO Stuff #############
        
"""


@app.route('/waitlist')
def notify_waitlist():
    if session.get("res_email"):
        session["access_granted_waitlist_page"] = True
    
    # Check if the session variable is set
    if not session.get("access_granted_waitlist_page"):
        abort(403, description="You cannot access this page the other time. Await for the opening of the access in the middle of June.")  # Forbidden
    
    # Clear the session variable after access
    session.pop("access_granted_waitlist_page", None)
    
    restaurant_email = session.get("verified_res_email")
    restaurant_name = session.get("restaurant_name")
    
    return render_template('wait_for_full_access/success.html', restaurant_email=restaurant_email, restaurant_name=restaurant_name, title="Waitlist Added")
    



#################### Registration/Login Part Start ####################

@app.route('/landing', methods=['GET', 'POST'])
def serve_landing():
    return render_template('start/bestLanding.html', title="Restaurant Assistant")



@app.route('/', methods=['GET', 'POST'])
def landing_page():
    #session.clear()  # Clear session for clean state testing
    #print("Session cleared")

    #if session.get("res_email"):
        #return redirect(url_for("notify_waitlist"))
    if os.environ.get("GO_TO_LAND_AT_START") == "True":
        return redirect("https://landing.mom-ai-restaurant.pro")
    
    """
    form = RestaurantForm()
    print("Form Created")

    if form.validate_on_submit():
        print("Pressed submit")

        session["email"] = form.email.data
        session["password"] = form.password.data

        if check_credentials(form.email.data, form.password.data, collection, for_login_redirect=True):
            flash('It seems that your email and password are already registered. Please log in.')
            return redirect(url_for('login'))

        restaurant_name = form.restaurant_name.data
        print(f"Restaurant name: {restaurant_name}")

        if form.restaurant_url.data:
            restaurant_url = form.restaurant_url.data
            print(f"Restaurant website URL: {restaurant_url}")
        else:
            restaurant_url = "No URL provided"

        #other_instructions = form.other_instructions.data
        #print(f"Other instructions: {other_instructions}")

        password = form.password.data
        #print(f"Restaurant password: {password}")

        location_coord = request.form['location']
        print(f"Location: {location_coord}")
        
        location_name = request.form['locationName']
        print(f"Location Name: {location_name}")

        session["location_coord"] = location_coord
        session["location_name"] = location_name

        #currency = form.currency.data
        #print(f"Currency of the restaurant: {currency}")

        currency = "EUR"

        session["currency"] = "EUR"

        # Save the image to GridFS
        image = form.image.data
        #print(f'Image Received:{image}')
        if image:
            filename = secure_filename(image.filename)
            file_id = fs.put(image, filename=filename)
            print(f'Raw file id {file_id} and string file id {str(file_id)}')
            session["logo_id"] = str(file_id)
        

        if request.files['menu']:
            menu = request.files['menu']
            #script = request.files['script']

            # Extract the original file extensions
            menu_extension = os.path.splitext(menu.filename)[1]
            #script_extension = os.path.splitext(script.filename)[1]

            menu_filename = secure_filename(f"menu_file{menu_extension}")
            #script_filename = secure_filename(f"script_file{script_extension}")

            # print(f"Menu filename: {menu_filename}")
            # print(f"Script filename: {script_filename}")

            menu_xlsx_path = os.path.join(app.config['UPLOAD_FOLDER'], menu_filename)
            #script_path = os.path.join(app.config['UPLOAD_FOLDER'], script_filename)
            # print(f"Menu xlsx path: {menu_xlsx_path}")
            # print(f"Script path: {script_path}")

            # Save the files
            menu.save(menu_xlsx_path)
            #script.save(script_path)
            # print("Files saved")

            menu_save_path = os.path.join(app.config['UPLOAD_FOLDER'], "menu_file.txt")
            
            menu_txt_path, html_menu = convert_xlsx_to_txt_and_menu_html(menu_xlsx_path, menu_save_path, currency)
            
            if not isinstance(menu_txt_path, str):
               print("Entered Invalid Menu Error.")
               flash(str(menu_txt_path))
               return redirect("/")
            # print(f"Generated menu txt file: {menu_txt_path}")

            session["restaurant_name"] = restaurant_name
            session["res_website_url"] = restaurant_url
            session["html_menu"] = html_menu       

            with open(menu_txt_path, 'rb') as menu_file:
                menu_encoded = base64.b64encode(menu_file.read())
                #script_encoded = base64.b64encode(script_file.read())
        
            #session["menu_encoded"] = menu_encoded
            #session["script_encoded"] = script_encoded

            print(f"\nMenu encoded: {menu_encoded}\n")
            #print(f"\nScript encoded: {script_encoded}\n")
            print("Files encoded")
            
            print(f"Menu TXT path passed {menu_txt_path}")

            assistant, menu_vector_id, menu_file_id = create_assistant(restaurant_name, currency, menu_txt_path, client=CLIENT_OPENAI)

            session['assistant_id'] = assistant.id
            session['menu_file_id'] = menu_file_id
            session['menu_vector_id'] = menu_vector_id

            messages = [{'sender': 'assistant', 'content': f'Hello! I am {restaurant_name}\'s Assistant! Talk to me!'}]
            session['messages'] = messages
            
            users_email = form.email.data

            session['res_email'] = users_email

            # Assume code generation and email sending are handled here
            generated_confirmation_code = generate_code()  # You need to implement this

            #print(mail)
            #print(users_email)
            #print(generated_confirmation_code)
            #print(FROM_EMAIL)

            send_confirmation_email(mail, users_email, generated_confirmation_code, FROM_EMAIL)  # Implement this
            session['expected_code'] = generated_confirmation_code  # Store in session for simplicity
            
            session["access_granted_email_enter_code"] = True

            # Save other form data as needed, then redirect to enter the code
            return redirect(url_for('enter_code'))


        
        session["password"] = password


        session["restaurant_name"] = restaurant_name
        session["res_website_url"] = restaurant_url        

        
        session["password"] = password

        #print(f"Files saved at {menu_txt_path} and {script_path}")
        
        #session["menu_encoded"] = menu_encoded
        #session["script_encoded"] = script_encoded

        assistant, menu_vector_id, menu_file_id = create_assistant(restaurant_name, currency, menu_path=None, client=CLIENT_OPENAI, menu_path_is_bool=False)
        session['assistant_id'] = assistant.id
        session['menu_vector_id'] = menu_vector_id
        session['menu_file_id'] = menu_file_id

        # Optionally, you can insert these details into a database here
        # insert_document(collection, restaurant_name, menu_encoded, script_encoded, assistant.id)
        
        '''
        if menu_path == script_path:
            os.remove(menu_path)
        else:    
            os.remove(menu_path)
            os.remove(script_path)
        print("Temporary files removed")
        '''
        
        messages = [{'sender': 'assistant', 'content': f'Hello! I am {restaurant_name}\'s Assistant! Talk to me!'}]
        session['messages'] = messages
        
        users_email = form.email.data

        session['res_email'] = users_email

        # Assume code generation and email sending are handled here
        generated_confirmation_code = generate_code()  # You need to implement this

        #print(mail)
        #print(users_email)
        #print(generated_confirmation_code)
        #print(FROM_EMAIL)

        send_confirmation_email(mail, users_email, generated_confirmation_code, FROM_EMAIL)  # Implement this
        session['expected_code'] = generated_confirmation_code  # Store in session for simplicity
        
        session["access_granted_email_enter_code"] = True

        # Save other form data as needed, then redirect to enter the code
        return redirect(url_for('enter_code'))


    else:
        if check_credentials(form.email.data, form.password.data, collection, for_login_redirect=True):
            flash('It seems that your email and password are already registered. Please log in.')
            return redirect(url_for('login'))
        # Output the errors
        for field, errors in form.errors.items():
            for error in errors[:1]:
                print(f"Error in field '{field}': {error}")
                flash(f"Error in field '{field}': {error}", 'error')
        print("Form not submitted or validation failed")
    

    if session.get("res_email") and session.get("password"):
        # Find the instance in MongoDB
        restaurant_instance = collection.find_one({"email": session.get("res_email")}) 
        if restaurant_instance:
            print(f"Found email {session.get('res_email')} and password {session.get('password')} in session")
            return redirect(url_for("dashboard_display"))
    """
    
            
    return render_template('start/bestLanding.html', title="AI Restaurant")

@app.route('/register', methods=['GET', 'POST'])
def register():
    referral_id = request.args.get("referral_id")

    form = RestaurantForm()
    print("Form Created")

    if form.validate_on_submit():
        print("Pressed submit")

        session["email"] = form.email.data
        session["password"] = form.password.data

        if check_credentials(form.email.data, form.password.data, collection, for_login_redirect=True):
            flash('It seems that your email and password are already registered. Please log in.')
            return redirect(url_for('login'))

        restaurant_name = form.restaurant_name.data
        print(f"Restaurant name: {restaurant_name}")

        if form.restaurant_url.data:
            restaurant_url = form.restaurant_url.data
            print(f"Restaurant website URL: {restaurant_url}")
        else:
            restaurant_url = "No URL provided"

        #other_instructions = form.other_instructions.data
        #print(f"Other instructions: {other_instructions}")

        password = form.password.data
        #print(f"Restaurant password: {password}")

        location_coord = request.form['location']
        print(f"Location: {location_coord}")
        
        location_name = request.form['locationName']
        print(f"Location Name: {location_name}")

        session["location_coord"] = location_coord
        session["location_name"] = location_name

        #currency = form.currency.data
        #print(f"Currency of the restaurant: {currency}")

        currency = "EUR"

        session["currency"] = "EUR"

        # Save the image to GridFS
        image = form.image.data
        #print(f'Image Received:{image}')
        if image:
            filename = secure_filename(image.filename)
            file_id = fs.put(image, filename=filename)
            print(f'Raw file id {file_id} and string file id {str(file_id)}')
            session["logo_id"] = str(file_id)
        
        if form.referral_id.data:
            session["id_of_who_referred"] = form.referral_id.data
        
        if request.files['menu']:
            menu = request.files['menu']
            #script = request.files['script']

            # Extract the original file extensions
            menu_extension = os.path.splitext(menu.filename)[1]
            #script_extension = os.path.splitext(script.filename)[1]

            menu_filename = secure_filename(f"menu_file{menu_extension}")
            #script_filename = secure_filename(f"script_file{script_extension}")

            # print(f"Menu filename: {menu_filename}")
            # print(f"Script filename: {script_filename}")

            menu_xlsx_path = os.path.join(app.config['UPLOAD_FOLDER'], menu_filename)
            #script_path = os.path.join(app.config['UPLOAD_FOLDER'], script_filename)
            # print(f"Menu xlsx path: {menu_xlsx_path}")
            # print(f"Script path: {script_path}")

            # Save the files
            menu.save(menu_xlsx_path)
            #script.save(script_path)
            # print("Files saved")

            menu_save_path = os.path.join(app.config['UPLOAD_FOLDER'], "menu_file.txt")
            
            menu_txt_path, html_menu = convert_xlsx_to_txt_and_menu_html(menu_xlsx_path, menu_save_path, currency)
            
            if not isinstance(menu_txt_path, str):
               print("Entered Invalid Menu Error.")
               flash(str(menu_txt_path))
               return redirect("/register")
            # print(f"Generated menu txt file: {menu_txt_path}")

            session["restaurant_name"] = restaurant_name
            session["res_website_url"] = restaurant_url
            session["html_menu"] = html_menu       

            with open(menu_txt_path, 'rb') as menu_file:
                menu_encoded = base64.b64encode(menu_file.read())
                #script_encoded = base64.b64encode(script_file.read())
        
            #session["menu_encoded"] = menu_encoded
            #session["script_encoded"] = script_encoded

            print(f"\nMenu encoded: {menu_encoded}\n")
            #print(f"\nScript encoded: {script_encoded}\n")
            print("Files encoded")
            
            print(f"Menu TXT path passed {menu_txt_path}")

            assistant, menu_vector_id, menu_file_id = create_assistant(restaurant_name, currency, menu_txt_path, client=CLIENT_OPENAI)

            unique_azz_id = restaurant_name.lower().strip().replace(" ", "_").replace("'","")+"_"+assistant.id[-4:]

            
            session['assistant_id'] = assistant.id
            session['menu_file_id'] = menu_file_id
            session['menu_vector_id'] = menu_vector_id
            session['unique_azz_id'] = unique_azz_id

            messages = [{'sender': 'assistant', 'content': f'Hello! I am {restaurant_name}\'s Assistant! Talk to me!'}]
            session['messages'] = messages
            
            users_email = form.email.data

            session['res_email'] = users_email

            # Assume code generation and email sending are handled here
            generated_confirmation_code = generate_code()  # You need to implement this

            #print(mail)
            #print(users_email)
            #print(generated_confirmation_code)
            #print(FROM_EMAIL)

            send_confirmation_email(mail, users_email, generated_confirmation_code, FROM_EMAIL)  # Implement this
            session['expected_code'] = generated_confirmation_code  # Store in session for simplicity
            
            session["access_granted_email_enter_code"] = True

            # Save other form data as needed, then redirect to enter the code
            return redirect(url_for('enter_code'))


        
        session["password"] = password


        session["restaurant_name"] = restaurant_name
        session["res_website_url"] = restaurant_url        

        
        session["password"] = password

        #print(f"Files saved at {menu_txt_path} and {script_path}")
        
        #session["menu_encoded"] = menu_encoded
        #session["script_encoded"] = script_encoded

        assistant, menu_vector_id, menu_file_id = create_assistant(restaurant_name, currency, menu_path=None, client=CLIENT_OPENAI, menu_path_is_bool=False)
        session['assistant_id'] = assistant.id
        session['menu_vector_id'] = menu_vector_id
        session['menu_file_id'] = menu_file_id

        unique_azz_id = restaurant_name.lower().strip().replace(" ", "_").replace("'","")+"_"+assistant.id[-4:]
        session["unique_azz_id"] = unique_azz_id
        
        print("We are right before qr code generation")

        qr_code_id = generate_qr_code_and_upload("https://mom-ai-restaurant.pro/assistant_order_chat/"+unique_azz_id) #assistant_code

        print(f"Type of qr code id: {type(qr_code_id)}")
        print("We are past qr code function")
        qr_code_id = str(qr_code_id)

        session["qr_code_id"] = qr_code_id

        # Optionally, you can insert these details into a database here
        # insert_document(collection, restaurant_name, menu_encoded, script_encoded, assistant.id)
        
        """
        if menu_path == script_path:
            os.remove(menu_path)
        else:    
            os.remove(menu_path)
            os.remove(script_path)
        print("Temporary files removed")
        """
        
        messages = [{'sender': 'assistant', 'content': f'Hello! I am {restaurant_name}\'s Assistant! Talk to me!'}]
        session['messages'] = messages
        
        users_email = form.email.data

        session['res_email'] = users_email

        # Assume code generation and email sending are handled here
        generated_confirmation_code = generate_code()  # You need to implement this

        #print(mail)
        #print(users_email)
        #print(generated_confirmation_code)
        #print(FROM_EMAIL)

        send_confirmation_email(mail, users_email, generated_confirmation_code, FROM_EMAIL)  # Implement this
        session['expected_code'] = generated_confirmation_code  # Store in session for simplicity
        
        session["access_granted_email_enter_code"] = True

        # Save other form data as needed, then redirect to enter the code
        return redirect(url_for('enter_code'))


    else:
        if check_credentials(form.email.data, form.password.data, collection, for_login_redirect=True):
            flash('It seems that your email and password are already registered. Please log in.')
            return redirect(url_for('login'))
        # Output the errors
        for field, errors in form.errors.items():
            for error in errors[:1]:
                print(f"Error in field '{field}': {error}")
                if "csrf" in error.lower():
                    flash(f"Error in field '{field}': {error} - PLEASE, RELOAD THE PAGE!", 'error')
        print("Form not submitted or validation failed")
    return render_template('start/register.html', form=form, title="Register", GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if os.environ.get("ALLOW_LOGIN", "False") != "True":
        abort(403)    
    form = LoginForm()
    if form.validate_on_submit():
        # Assuming a function `check_credentials` to validate user login
        if check_credentials(form.email.data, form.password.data, collection):
            user = collection.find_one({'email': form.email.data})
            session["res_email"] = user.get('email')
            session["password"] = user.get('password')
            print('You have been successfully logged in!')
            flash('You have been successfully logged in!')
            return redirect(url_for('dashboard_display'))
        else:
            print('Login failed. Check your email and password.')
            flash('Login failed. Check your email and password.')
            return redirect(url_for('login'))
    return render_template('start/login.html', form=form, title="Login", GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Clear the session
    flash('You logged out successfully')  # Add a flash message
    return redirect(url_for('login'))  # Redirect to dashboard

#################### Registration/Login Part End ####################

#################### Blog Posts #########################
@app.route('/post/<string:url_slug>')
def post(url_slug):
    post = Post.query.filter_by(url_slug=url_slug).first_or_404()
    title = post.title.replace('(', '').replace(')', '').replace("'", '')
    content = post.content
    created_at = post.created_at.strftime('%d.%m.%Y %H:%M')
    return render_template('blog-posts/post.html', content=content, title=title, created_at=created_at)

                           

@app.route('/all_posts')
def all_posts():
    page = request.args.get('page', 1, type=int)
    posts_pagination = Post.query.paginate(page=page, per_page=10, count=False)
    posts = posts_pagination.items
    
    post_data = []
    for post in posts:
        # Parse the HTML content
        soup = BeautifulSoup(post.content, 'html.parser')
        
        # Remove all h1 elements
        for h1 in soup.find_all('h1'):
            h1.decompose()
        
        # Extract plain text
        plain_text = soup.get_text()
        
        # Remove text within brackets
        plain_text = re.sub(r'\(.*?\)', '', plain_text)
        
        # Get the first 100 characters of the plain text
        excerpt = plain_text[:300]
        
        post_data.append({
            'title': post.title,
            'excerpt': excerpt,
            'link': url_for('post', url_slug=post.url_slug),
            'created_at': post.created_at.strftime('%d.%m.%Y %H:%M')  # Format the created_at field
        })
    
    next_url = url_for('all_posts', page=posts_pagination.next_num) if posts_pagination.has_next else None
    prev_url = url_for('all_posts', page=posts_pagination.prev_num) if posts_pagination.has_prev else None
    
    return render_template('blog-posts/all_posts.html', posts=post_data, title="Blog Posts", next_url=next_url, prev_url=prev_url)


"""
@app.route('/add_post', methods=['POST'])
@auth.login_required
def add_post():
    data = request.json
    content = data.get('content')
    title = data.get('title')
    
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    new_post = Post(title=title, content=content)
    db.session.add(new_post)
    db.session.commit()
    
    return jsonify({'message': 'Post added successfully', 'title': title}), 201
"""




@app.route('/image/<file_id>')
def serve_image(file_id):
    try:
        file_id = ObjectId(file_id)  # Convert string file_id back to ObjectId
        grid_out = fs.get(file_id)
        return send_file(io.BytesIO(grid_out.read()), download_name=grid_out.filename, mimetype='image/jpeg')
    except Exception as e:
        print(e)
        abort(404)



#################### Email Confirmation Part Start ####################

@app.route('/set_session_and_redirect')
def set_session_and_redirect():
    # Set the session variable
    session['access_granted_email_enter_code_full'] = True
    generated_confirmation_code = generate_code()
    session["expected_code"] = generated_confirmation_code
    print("Setup expected code in session")
    # Redirect to the target URL
    return redirect(url_for('enter_code_full', initial_sending='yeaaah'))

@app.route('/enter_code_full', methods=['GET', 'POST'])
def enter_code_full():
    # Check if the session variable is set
    if not session.get('access_granted_email_enter_code_full'):
        abort(403)  # Forbidden
    
    res_email = session.get("restaurant_email")
    
    generated_confirmation_code = session.get("expected_code")
    
    send_confirmation_email(mail, res_email, generated_confirmation_code, FROM_EMAIL)
    form = ConfirmationForm()  # Assume you have a simple form for this
    if form.validate_on_submit():
        user_code = form.confirmation_code.data
        if session.get('expected_code'):
            if user_code == session.get('expected_code'):
                # Clear the session variable after access
                session.pop('access_granted_email_enter_code', None)
                session['access_granted_change_credentials'] = True
                return redirect(url_for('change_credentials', res_email=res_email))
            else:
                flash('Invalid confirmation code. Please try again.', 'error')

    return render_template('email_confirm/enter_code_full.html', form=form, res_email=res_email, title="Enter Confirmation Code")


@app.route('/enter_code_full2', methods=['GET', 'POST'])
def enter_code_full2():
    # Check if the session variable is set
    if not session.get('access_granted_email_enter_code_full'):
        abort(403)  # Forbidden
    
    res_email = session.get("restaurant_email")

    
    generated_confirmation_code = session.get("expected_code")
    
    send_confirmation_email(mail, res_email, generated_confirmation_code, FROM_EMAIL)
    form = ConfirmationForm()  # Assume you have a simple form for this
    if form.validate_on_submit():
        user_code = form.confirmation_code.data
        if session.get('expected_code'):
            if user_code == session.get('expected_code'):
                # Clear the session variable after access
                session.pop('access_granted_email_enter_code', None)
                session.pop("access_granted_email_password_change_page")
                session.pop('access_granted_change_credentials')
                return redirect(url_for('dashboard_display'))
            else:
                flash('Invalid confirmation code. Please try again.', 'error')

    return render_template('email_confirm/enter_code_full2.html', form=form, res_email=res_email, title="Enter Confirmation Code")


@app.route('/change_credentials', methods=['GET', 'POST'])
def change_credentials():
    
    # Check if the session variable is set
    if not session.get('access_granted_change_credentials'):
        abort(403)  # Forbidden
    
    form = ChangeCredentialsForm()
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_email = form.new_email.data
        new_password = form.new_password.data

        user = collection.find_one({"unique_azz_id":session.get("unique_azz_id")})
        
        stored_password = user["password"]

        # Decode the stored password from bytes to string if necessary
        #if isinstance(stored_password, bytes):
            #stored_password = stored_password.decode("utf-8")
            #print(f"Decoded stored password: {stored_password}")

        # Ensure stored_password is in the correct format
        #if not stored_password.startswith('$2b$'):
            #raise ValueError("Stored password is not in the correct format.")
        
        if bcrypt.checkpw(current_password.encode("utf-8"), stored_password):
            updates = {}
            if not new_email:
                go_next = "dashboard_display"
            else:
                go_next = "enter_code_full2"
            if new_email:
                # Query the database and project only the 'email' field
                emails_cursor = collection.find({}, {"email": 1, "_id": 0})

                # Collect emails in a list
                emails = [doc["email"] for doc in emails_cursor]
                if new_email in emails:
                    flash("Oops, your email address is popular! Some other account is registered on it. Use the other one.")
                    return redirect(url_for("change_credentials"))
                updates['email'] = new_email
                session["restaurant_email"] = new_email
            if new_password:
                updates['password'] = hash_password(new_password)

            if updates:
                collection.update_one({"unique_azz_id":session.get("unique_azz_id")}, {"$set": updates})  
                flash('Credentials updated successfully!', 'success')
                return redirect(url_for(go_next))
            else:
                flash('No changes were made.', 'info')
                return redirect(url_for("dashboard_display"))
        else:
            flash('Current password is incorrect.', 'danger')

        return redirect(url_for('change_credentials'))
    
    return render_template('settings/change_credentials.html', form=form, title="Change Credentials")



@app.route('/add-email-in-funnel', methods=['POST'])
def add_email_in_funnel():
    data = request.json
    email = data.get("email")

    msg_body = f"""
    <p style="font-size: 16px; line-height: 1.5;">Thank you for trusting MOM AI Restaurant. From now on you are on the frontier of AI-innvation in the restaurant industry!</p>
    <p style="font-size: 16px; line-height: 1.5;">By the way, you can reap benefits of AI in your restaurant after this <a href="https://mom-ai-restaurant.pro/register" style="color:#000033"><u>simple 5-minutes registration.</u></a></p>
    """

    subject_line = "Ride the wave of the innovation with MOM AI Restaurant"
    
    send_email_raw(mail, email, msg_body, subject_line, FROM_EMAIL)

    # The URL to which the POST request will be sent
    url = 'https://script.google.com/macros/s/AKfycbww4HXvT1pArfTYZZHSkryqPPgXPmPZf44skGWwzsz0DHmQn_8ViSTIWbGnkQciZBbg/exec'

    timestamp_utc = datetime.utcnow().strftime('%d.%m.%Y %H:%M')

    # The data to be sent in the POST request
    data = {
        "gid":2141419829,
        "email": email,
        'time': timestamp_utc
    }

    # Sending the POST request
    response = requests.post(url, data=data)

    return jsonify({"ok":True})


@app.route('/send-orderid-email', methods=['POST', 'GET'])
def send_orderid_email():
    data = request.json
    email = data.get("email")
    restaurant_name = data.get("restaurant_name")
    order_id = data.get("order_id")

    msg_body = f"""
    <p style="font-size: 16px; line-height: 1.5;">Thank you for ordering at {restaurant_name} with MOM AI Restaurant.<br><br>
    Provide this order ID in the restaurant and have a great meal!</p>
    <div style="text-align: center; font-size: 24px; margin: 20px 0;">
                <strong style="background-color: #f0f0f0; padding: 10px; border-radius: 4px;">{order_id}</strong>
    </div>
    """

    subject_line = "Your Order ID from MOM AI Restaurant"
    
    send_email_raw(mail, email, msg_body, subject_line, FROM_EMAIL)

    # The URL to which the POST request will be sent
    url = 'https://script.google.com/macros/s/AKfycbww4HXvT1pArfTYZZHSkryqPPgXPmPZf44skGWwzsz0DHmQn_8ViSTIWbGnkQciZBbg/exec'

    timestamp_utc = datetime.utcnow().strftime('%d.%m.%Y %H:%M')

    # The data to be sent in the POST request
    data = {
        "gid":2010883790,
        "email": email,
        'time': timestamp_utc
    }

    # Sending the POST request
    response = requests.post(url, data=data)

    return jsonify({"ok":True})



@app.route('/enter_code', methods=['GET', 'POST'])
def enter_code():
    # Check if the session variable is set
    if not session.get('access_granted_email_enter_code'):
        abort(403)  # Forbidden
    
    print("Entered enter_code")
    res_email = session.get('res_email')
    form = ConfirmationForm()  # Assume you have a simple form for this
    if form.validate_on_submit():
        user_code = form.confirmation_code.data
        if session.get('expected_code'):
            if user_code == session.get('expected_code'):
                # Clear the session variable after access
                session.pop('access_granted_email_enter_code', None)
                session["access_granted_email_confirm_page"] = True
                return redirect(url_for('confirm_email', res_email=res_email))
            else:
                flash('Invalid confirmation code. Please try again.', 'error')

    return render_template('email_confirm/enter_code.html', form=form, res_email=res_email, title="Enter Confirmation Code")



@app.route('/confirm_email/<res_email>')
def confirm_email(res_email):
    # Check if the session variable is set
    if not session.get('access_granted_email_confirm_page'):
        abort(403)  # Forbidden
    
    # Clear the session variable after access
    session.pop('access_granted_email_confirm_page', None)

    #session["res_email"] = session.get("verified_res_email")

    res_name = session.get("restaurant_name", "name_placeholder")
    print(f"Restaurant Name: {res_name}")

    #menu_file = session.get("menu_encoded", "menu_placeholder")
    #print(f"Menu File: {menu_file}")

    #script_file = session.get("script_encoded", "script_placeholder")
    #print(f"Script File: {script_file}")

    assistant_id = session.get("assistant_id", "assistant_id_placeholder")
    print(f"Assistant ID: {assistant_id}")

    res_password = session.get("password", "password_placeholder")
    print(f"Restaurant Password: {res_password}")

    #verified_res_email = session.get("verified_res_email", "email_placeholder")

    restaurant_name = session.get("restaurant_name")
    
    website_url = session.get("res_website_url", "Restaurant URL placeholder")

    menu_file_id = session.get("menu_file_id")
    menu_vector_id = session.get("menu_vector_id")

    currency = session.get("currency")
    html_menu = session.get("html_menu", MOM_AI_EXEMPLARY_MENU_HTML)

    file_id = session.get("logo_id", "666af654dee400a1d635eb08")

    qr_code_id = session.get("qr_code_id")

    hashed_res_password = hash_password(res_password)

    session["hashed_res_passord"] = hashed_res_password

    location_coord = session["location_coord"]
    location_name = session["location_name"]

    unique_azz_id = session.get("unique_azz_id")
    print("Unique azz id we insert, ", unique_azz_id)
    id_of_who_referred = session.get("id_of_who_referred")

    # Add referee to the referees' list of the referral
    if id_of_who_referred:
        print("id of who referred found")
        collection.update_one({"referral_code": id_of_who_referred}, {"$push":{"referees": unique_azz_id}})
    
    insert_restaurant(collection, res_name, unique_azz_id, res_email, hashed_res_password, website_url, assistant_id, menu_file_id, menu_vector_id, currency, html_menu, qr_code=qr_code_id, wallet_public_key_address="None", wallet_private_key="None", location_coord=location_coord, location_name=location_name, id_of_who_referred=id_of_who_referred, logo_id=file_id)
    send_confirmation_email_registered(mail, res_email, restaurant_name, FROM_EMAIL)
    print("Confirmation of registarion Email has been sent and the account created.\n\n")
    print(f"Setup hashed res password in session:{hashed_res_password}")
    
    session["verified_res_email"] = session.get("res_email", "placeholder_email")
    # Example: mark user as 'email_verified' in your database
    session["access_granted_assistant_demo_chat"] = True

    return render_template('email_confirm/confirm_email.html', title="Email Confirmed")  # Confirmation success page


#################### Email Confirmation Part End ####################







#################### Payment Setup Part Start ####################

"""
@app.route('/payments_setup', methods=['GET', 'POST'])
def setup_web_payments():
    session["verified_res_email"] = session.get("res_email", "placeholder_email")
    return render_template("create_web3_wallet.html", restaurant_name=session.get("restaurant_name", "Matronins placeholder"))




@app.route('/create_wallet', methods=['POST', 'GET'])
def create_web_wallet():

    data = request.form
    
    assistant_id = session.get('assistant_id', 'No assistant ID available')

    web3_wallet_address, web3_private_key = create_web3_wallet()
    print(f"Address: {web3_wallet_address}")
    print(f"Private Key: {web3_private_key}")

    res_name = session.get("restaurant_name", "name_placeholder")
    print(f"Restaurant Name: {res_name}")

    menu_file = session.get("menu_encoded", "menu_placeholder")
    print(f"Menu File: {menu_file}")

    script_file = session.get("script_encoded", "script_placeholder")
    print(f"Script File: {script_file}")

    assistant_id = session.get("assistant_id", "assistant_id_placeholder")
    print(f"Assistant ID: {assistant_id}")

    res_password = session.get("password", "password_placeholder")
    print(f"Restaurant Password: {res_password}")

    verified_res_email = session.get("verified_res_email", "email_placeholder")

    website_url = session.get("res_website_url", "Restaurant URL placeholder")

    #insert_document(collection, res_name, verified_res_email, res_password, website_url, assistant_id, web3_wallet_address, web3_private_key)

    return render_template("register_finish.html", restaurant_name = res_name, web3_wallet_address = web3_wallet_address, title="Registration Complete")

#################### Payment Setup Part End ####################
"""






#################### Demo Chat Part Start ####################

@app.route('/assistant_demo_chat', methods=['POST', 'GET'])
def assistant_demo_chat():
    
    # Check if the session variable is set
    #if not session.get('access_granted_assistant_demo_chat'):
        #abort(403)  # Forbidden
    
    print(request.form)
    data = request.form
    user_message = 'Customer\'s message example'
    
    #ai_assist_response = get_assistants_response(user_message)

    messages = session.get('messages')

    print(len(messages))

    #if len(messages) >= 4:
        #return redirect(url_for("setup_web_payments"))
    
    #response = get_assistants_response(user_message, CLIENT_OPENAI)

    if user_message:
        messages.append({'sender': 'user', 'content': user_message})
        # Simulate the assistant's response
        messages.append({'sender': 'assistant', 'content': "I do not know what to say as I am not an AI yet. But in 7 seconds you will be redirected and magic will happen."})
    
    session['messages'] = messages
    print(messages)

    #send_waitlist_email(mail, verified_res_email, restaurant_name, FROM_EMAIL)

    # Clear the session variable after access
    session.pop('access_granted_assistant_demo_chat', None)
    restaurant_name = session.get('restaurant_name')
      
    session["access_granted_waitlist_page"] = True
    
    return render_template("start/demo.html", title="Demo Chat", messages=messages, restaurant_name=restaurant_name)

#################### Demo Chat Part End ####################





#################### Dashboard Part Main App ####################

@app.route('/ai-restaurants')
def market_dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 12  # 2 columns * 6 rows
    search_query = request.args.get('location', '')
    if search_query:
        title = f"Best AI-empowered restaurants in {search_query}"
    else:
        title = "Best AI-empowered restaurants search"
    restaurants, total = get_restaurants(page, per_page, search_query)  # Function to fetch paginated restaurant data
    return render_template('marketing_dashboard/market_dashboard.html', restaurants=restaurants, page=page, per_page=per_page, total=total, title=title, search_query=search_query, GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY)

def get_restaurants(page, per_page, search_query=''):
    skip = (page - 1) * per_page
    cursor = collection.find()
    total = collection.count_documents({})
    restaurants = list(cursor)
    
    if search_query:
        search_terms = [term.strip().lower() for term in search_query.split(',')]
        filtered_restaurants = [r for r in restaurants if any(term in r.get('location_name', '').lower() for term in search_terms) and r.get('profile_visible', False)]
    else:
        filtered_restaurants = [r for r in restaurants if r.get('profile_visible', True)]

    total = len(filtered_restaurants)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_restaurants = filtered_restaurants[start:end]

    return paginated_restaurants, total


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard_display():
    if request.args.get("show_popup") == "True":
        show_popup = True
    else:
        show_popup = False
      
    PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID")

    print("Jumped on display dashboard link")
    res_email = session.get("res_email")
    res_password = session.get("password")

    hashed_res_password = session.get("hashed_res_password")
    print(f"hashed_res_password on dashboard {hashed_res_password}")

    # Find the instance in MongoDB
    restaurant_instance = collection.find_one({"email": res_email}) 

    # Check if the instance exists
    if restaurant_instance:
        # Retrieve the necessary values from the instance
        restaurant_name = restaurant_instance.get("name")
        restaurant_website_url = restaurant_instance.get("website_url")
        restaurant_email = restaurant_instance.get("email")
        assistant_id = restaurant_instance.get("assistant_id")
        web3_wallet_address = restaurant_instance.get("web3_wallet_address")
        current_balance = restaurant_instance.get("balance")
        res_unique_azz_id = restaurant_instance.get("unique_azz_id")
        awaiting_withdrawal = restaurant_instance.get("await_withdrawal")
        res_currency = restaurant_instance.get("res_currency")
        html_menu = restaurant_instance.get("html_menu")
        assistant_spent = restaurant_instance.get("assistant_fund")
        logo_id = restaurant_instance.get("res_logo", "666af654dee400a1d635eb08")
        qr_code_id = restaurant_instance.get("qr_code", "666af654dee400a1d635eb08")
        gateway_is_on = restaurant_instance.get("paymentGatewayTurnedOn")
        #subscription_number = restaurant_instance.get("subscription_number")

        #subscription_activated = True if get_subscription_status(subscription_number) == "ACTIVE" else False
        #print(f"Subscription Activated {subscription_activated}")
        #if not subscription_activated:
            #collection.update_one({"unique_azz_id":res_unique_azz_id}, {"$set":{"assistant_turned_on": False}})
        assistant_turned_on = restaurant_instance.get("assistant_turned_on")
        print(f"assistant turned on dashboard upload:{assistant_turned_on}")
        if not awaiting_withdrawal:
            awaiting_withdrawal = 0
         
        #session["subscription_activated"] = subscription_activated
        session["assistant_id"] = assistant_id
        session["restaurant_name"] = restaurant_name
        session["restaurant_email"] = restaurant_email
        session["current_balance"] = current_balance
        session["unique_azz_id"] = res_unique_azz_id
        session["res_currency"] = res_currency
        session["html_menu"] = html_menu
        session["qr_code_id"] = qr_code_id

        print(f"Assistant ID added in session: {assistant_id}")
        print(f"Restaurant name added in session: {restaurant_name}")
        
        if logo_id == None:
            logo_id = "666af654dee400a1d635eb08"
        
        logo_url = url_for('serve_image', file_id=logo_id)

    else:
        # Handle the case when the instance is not found
        flash("Restaurant not found. Please, login with the right credentials.")
        return redirect(url_for("login"))
    return render_template("dashboard/dashboard.html", title=f"{restaurant_name}\'s Dashboard", 
                           restaurant_name=restaurant_name, 
                           current_balance=f"{round(float(current_balance),2):.2f}", 
                           wallet_address=web3_wallet_address, 
                           email=restaurant_email, 
                           assistant_id=assistant_id,
                           restaurant_email=restaurant_email,
                           res_website_url = restaurant_website_url,
                           res_unique_azz_id=res_unique_azz_id,
                           awaiting_withdrawal=awaiting_withdrawal,
                           assistant_spent=f"{round(float(assistant_spent),2):.2f}",
                           res_currency=res_currency,
                           assistant_turned_on=assistant_turned_on,
                           logo_url=logo_url,
                           restaurant=restaurant_instance,
                           exchange_api_key=EXCHANGE_API_KEY,
                           gateway_is_on=gateway_is_on,
                           show_popup=show_popup,
                           PAYPAL_CLIENT_ID=PAYPAL_CLIENT_ID)

###################################### Dashboard Buttons ######################################

@app.route('/payments', methods=['POST', 'GET'])
def payments_display():
    
    #restaurant_name = session.get("restaurant_name")
    #restaurant_email = session.get("restaurant_email")
    unique_azz_id = session.get("unique_azz_id")

    restaurant = collection.find_one({"unique_azz_id":unique_azz_id})
    #print(restaurant)
    
    order_dashboard_id = unique_azz_id

    orders = db_order_dashboard[order_dashboard_id].find()

    payments = list(orders)

    print("Payments passed: ", payments)

    there_are_payments = True if len(payments)>=1 else False

    print(f"\n\nPayments Retrieved\n\n")

    #payments = [{"timestamp":order.get("timestamp"), "total_paid":order.get("total_paid"), ""} for order in orders]

    return render_template("dashboard/payments_history.html", payments=payments, restaurant=restaurant, there_are_payments=there_are_payments)

@app.route('/profile')
def show_restaurant_profile():
    # Retrieve restaurant profile by unique_azz_id
    unique_azz_id = session.get("unique_azz_id")
    restaurant = collection.find_one({'unique_azz_id': unique_azz_id})
    restaurant_balance = round(restaurant.get("balance"), 2)
    connected_chats_len = len(restaurant.get("notif_destin", []))
    if restaurant:
        return render_template('dashboard/profile.html', restaurant=restaurant, restaurant_balance=restaurant_balance, connected_chats=connected_chats_len, unique_azz_id=unique_azz_id)
    else:
        return "Restaurant not found", 404

@app.route('/assistant_toggler', methods=['POST'])
def toggle_assistant():
    data = request.get_json()
    assistant_turned_on = data.get('assistant_turned_on')
    print(f"Assistant turned on: {assistant_turned_on}")

    unique_azz_id = session.get("unique_azz_id")
    print(unique_azz_id)
    collection.update_one({"unique_azz_id":unique_azz_id}, {"$set":{"assistant_turned_on":assistant_turned_on}})
    
    # Respond with the new state
    return jsonify({'assistant_turned_on': assistant_turned_on})

@app.route('/payment_gateway_toggler', methods=['POST'])
def toggle_payment_gateway():
    data = request.get_json()
    print(data)
    paymentGatewayTurnedOn = data.get('payment_gateway_turned_on')
    print(f"Payment Gateway toggled: {paymentGatewayTurnedOn}")

    unique_azz_id = session.get("unique_azz_id")
    print(unique_azz_id)
    collection.update_one({"unique_azz_id":unique_azz_id}, {"$set":{"paymentGatewayTurnedOn":paymentGatewayTurnedOn}})
    
    # Respond with the new state
    return jsonify({'paymentGatewayTurnedOn': paymentGatewayTurnedOn})

@app.route('/profile_visibility_toggler', methods=['POST'])
def toggle_profile_visibility():
    data = request.get_json()
    profile_visible = data.get('profile_visible')
    print(f"Profile visible: {profile_visible}")

    unique_azz_id = session.get("unique_azz_id")
    print(unique_azz_id)
    collection.update_one({"unique_azz_id":unique_azz_id}, {"$set":{"profile_visible":profile_visible}})
    
    # Respond with the new state
    return jsonify({'profile_visible': profile_visible})

@app.route('/add_fee_payment_toggler', methods=['POST'])
def toggle_add_fee_payment():
    data = request.get_json()
    add_fee_payment = data.get('add_fee_payment')
    print(f"add_fee_payment: {add_fee_payment}")

    unique_azz_id = session.get("unique_azz_id")
    print(unique_azz_id)
    collection.update_one({"unique_azz_id":unique_azz_id}, {"$set":{"addFees":add_fee_payment}})
    
    # Respond with the new state
    return jsonify({'add_fee_payment': add_fee_payment})


'''
@app.route('/payment_gateway_toggler', methods=['POST'])
def toggle_payment_gateway():
    data = request.get_json()
    assistant_turned_on = data.get('assistant_turned_on')
    print(f"Assistant turned on: {assistant_turned_on}")

    unique_azz_id = session.get("unique_azz_id")
    print(unique_azz_id)
    collection.update_one({"unique_azz_id":unique_azz_id}, {"$set":{"assistant_turned_on":assistant_turned_on}})
    
    # Respond with the new state
    return jsonify({'assistant_turned_on': assistant_turned_on})
'''
    
@app.route('/profile_update/<attribute>', methods=['GET','POST'])
def update_profile(attribute):
    form = RestaurantFormUpdate()
    print(request.form)
    print(f"Request files: {request.files}")
    current_uni_azz_id = session.get("unique_azz_id")
    restaurant = collection.find_one({'unique_azz_id': current_uni_azz_id})
    #print(restaurant.get(attribute, "nope"))
    if form.validate_on_submit():
        new_value = request.form.get(attribute) or request.files.get(attribute)
        if not new_value:
            flash("No value provided - please, provide the data and submit again", 'danger')
            return redirect(url_for('update_profile', attribute=attribute))
        if attribute == 'name' and new_value:
            collection.update_one({'unique_azz_id': current_uni_azz_id}, {'$set': {'name': new_value}})
        elif attribute == 'website_url' and new_value:
            collection.update_one({'unique_azz_id': current_uni_azz_id}, {'$set': {'website_url': new_value}})
        elif attribute == 'description' and new_value:
            collection.update_one({'unique_azz_id': current_uni_azz_id}, {'$set': {'description': new_value}})    
        elif attribute == 'notif_destin' and new_value:
            collection.update_one({'unique_azz_id': current_uni_azz_id},{'$push': {'notif_destin': new_value}})
            NEW_CHAT_MESSAGE = f"🔝You are the best\n\nYou have successfully setup notifications!\n\nMOM AI bot will notify you upon upcoming of new orders in this chat.\n\nNow you should go to the 'Assistant' tab and start using your MOM AI Restaurant Assistant!"
            send_telegram_notification(new_value, message=NEW_CHAT_MESSAGE)
        elif attribute == 'pp_account' and new_value:
            if restaurant.get('pp_account', "nope") == "nope":
               collection.update_one({'unique_azz_id': current_uni_azz_id}, {'$set': {'earned_on_own_paypal':0}})
            pp_client_id = new_value.split("___")[0]
            pp_client_secret = new_value.split("___")[1]
            collection.update_one({'unique_azz_id': current_uni_azz_id}, {'$set': {'pp_client_id': pp_client_id, 'pp_client_secret':pp_client_secret}})
        # Image upload handling
        elif attribute == 'image' and form.image.data:
            image = form.image.data
            filename = secure_filename(image.filename)
            file_id = fs.put(image, filename=filename)
            print(f'Raw file id {file_id} and string file id {str(file_id)}')
            collection.update_one({'unique_azz_id': current_uni_azz_id}, {'$set': {'res_logo': file_id}})   
        
        print('Profile updated successfully!')
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard_display'))
    else:
        print('Error in form submission!')
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in the {getattr(form, field).label.text} field - {error}", 'danger')
                print(f"Error in the {getattr(form, field).label.text} field - {error}")
    return render_template('settings/profile_update.html', form=form, attribute=attribute, restaurant=restaurant, title="Update Profile")

@app.route('/set-working-hours')
def set_working_hours():
    current_uni_azz_id = session.get("unique_azz_id")
    restaurant = collection.find_one({'unique_azz_id': current_uni_azz_id})

    start_hours = restaurant["start_work"]
    end_hours = restaurant["end_work"]

    current_rest_timezone = restaurant.get('timezone', None)
    print(f"Current restaurant timezone: ", current_rest_timezone)

    return render_template('settings/set_working_hours.html', title="Set Working Hours", start_hours=start_hours, end_hours=end_hours, restaurant=restaurant, current_rest_timezone=current_rest_timezone)


@app.route('/submit_hours', methods=['POST'])
def submit_hours():
    working_hours = request.json['schedule']
    timezone = request.json['timezone']
    # Process the working hours as needed
    # For now, we'll just print them
    print(working_hours)
    current_uni_azz_id = session.get("unique_azz_id")
    restaurant = collection.find_one({'unique_azz_id': current_uni_azz_id})
    
    start_values = []
    end_values = []
    
    for day, times in working_hours.items():
        start_values.append(times['start'])
        end_values.append(times['end'])
    result = collection.update_one({'unique_azz_id': current_uni_azz_id}, {'$set':{"start_work":start_values, "end_work":end_values, "timezone":timezone}})
    print("\nUpdated successfully\n")
    flash("The working hours were updated successfully")

    return jsonify({"status": "success", "data": working_hours}), 200


@app.route('/submit_review', methods=['POST'])
def submit_review():
    data = request.json
    print(data)
    order_id = data.get("order_id")
    person_name = data.get("name")
    review_text = data.get("review_text")
    unique_azz_id = data.get("unique_azz_id")
    review_rating = data.get("rating")
    wallet_address = data.get("wallet_address", None)

    ### Validation Part ###

    try:
        # Query the database and project only the 'orderID' field
        orderids_cursor = db_order_dashboard[unique_azz_id].find({}, {"orderID": 1, "_id": 0})
        print(orderids_cursor)
        
        # Collect orderIDs in a list
        orderids = [doc["orderID"] for doc in orderids_cursor]
        print(orderids)
    except Exception as e:
        return jsonify({"message":"The Order ID is not existent", "success":False})
    

    if not order_id in orderids:
        print("No order ID in orders")
        return jsonify({"message":"The Order ID is not existent", "success":False})
    
    try:
        restaurant_reviews = db_rest_reviews[unique_azz_id]
        
        # Query the database and project only the 'orderID' field
        orderids_cursor_reviews = restaurant_reviews.find({}, {"order_id": 1, "_id": 0})

        # Collect orderIDs in a list
        orderids_reviews = [doc["order_id"] for doc in orderids_cursor_reviews]
    except Exception as e:
        orderids_reviews = []
        pass
    
    if order_id in orderids_reviews:
        print("The review is already there!")
        return jsonify({"message":"The review for this order has been already submitted", "success":False})

    
    # Success - adding review and topping up the web3 wallet
    
    review_to_pass = {
        "text": review_text,
        "person": person_name,
        "order_id": order_id,
        "rating": int(review_rating)
    }
    
    tx_hash = ""

    print("Order ID reviews: ", orderids_reviews)

    if wallet_address:
        # Check whether the review is gonna be the first one
        if len(orderids_reviews) == 0:
            amount_to_send = 150
        else:
            amount_to_send = 50

        tx = mint_and_send_tokens(wallet_address, amount_to_send)
        tx_hash = tx["tx_hash"]
        print(f"Sent {amount_to_send} MOM to the user")
    
    restaurant_reviews.insert_one(review_to_pass)

    if tx_hash:
        return jsonify({"message":f"The review has been successfully placed and token added to your balance.\nCheck the transaction on https://amoy.polygonscan.com/tx/{tx_hash}", "tx_hash":tx_hash, "success":True})
    else:
        return jsonify({"message":f"The review has been successfully placed and token added to your balance.", "tx_hash":tx_hash, "success":True})

@app.route('/settings', methods=['POST', 'GET'])
def settings_display():
    return render_template("dashboard/settings.html")
'''
@app.route('/add_number_nots', methods=['POST', 'GET'])
def add_number_nots():
    if request.method == 'POST':
        number = request.form['number']
        
        unique_azz_id = session.get("unique_azz_id")

        # Find the user and update the 'notif_destin' attribute
        collection.update_one(
            {'unique_azz_id': unique_azz_id},
            {'$push': {'notif_destin': number}}
        )
        return jsonify({"response":"success"})
'''

@app.route('/menu', methods=['POST', 'GET'])
def show_menu():
    form = UpdateMenuForm()
    html_menu = session.get("html_menu")
    wrapped_html_table = wrap_images_in_html_table(html_menu)

    print("That's the menu we've got ", wrapped_html_table)
    return render_template("dashboard/menu_display.html", html_menu=wrapped_html_table, form=form)


def wrap_images_in_html_table(html_table):
    soup = BeautifulSoup(html_table, 'html.parser')
    rows = soup.find_all('tr')[1:]  # Skip the header row

    try:
        for row in rows:
            cells = row.find_all('td')
            image_cell = cells[3]
            image_url = image_cell.text.strip()
            item_name = cells[0].text.strip()
            new_image_tag = f'<img src="{image_url}" alt="Image of {item_name}" width="170" height="auto">'
            image_cell.string = ""
            image_cell.append(BeautifulSoup(new_image_tag, 'html.parser'))

        return str(soup)
    except Exception as e:
        return html_table


@app.route('/update_menu', methods=['POST'])
def update_menu():
    print(request)
    menu = request.files['menu_update']
    #script = request.files['script']

    # Extract the original file extensions
    menu_extension = os.path.splitext(menu.filename)[1]
    #script_extension = os.path.splitext(script.filename)[1]

    menu_filename = secure_filename(f"menu_file{menu_extension}")
    #script_filename = secure_filename(f"script_file{script_extension}")

    print(f"Menu filename: {menu_filename}")
    #print(f"Script filename: {script_filename}")

    menu_xlsx_path = os.path.join(app.config['UPLOAD_FOLDER'], menu_filename)
    #script_path = os.path.join(app.config['UPLOAD_FOLDER'], script_filename)
    print(f"Menu xlsx path: {menu_xlsx_path}")
    #print(f"Script path: {script_path}")

    # Save the files
    menu.save(menu_xlsx_path)
    #script.save(script_path)
    print("Files saved")

    menu_save_txt_path = os.path.join(app.config['UPLOAD_FOLDER'], "menu_file.txt")
  
    currency = session.get("res_currency")
    restaurant_name = session.get("restaurant_name")
    unique_azz_id = session.get("unique_azz_id")
    assistant_id = session.get("assistant_id")

    upload_response = upload_new_menu(menu_xlsx_path, menu_save_txt_path, currency, restaurant_name, collection, unique_azz_id, assistant_id)
    print(upload_response)
    
    if upload_response["success"]:
        flash("Menu updated successfully!", category="success")
    else:
        flash("Error updating menu. Please check the file for validity.", category="danger")

    return redirect(url_for("dashboard_display"))



# Mint MOM token
@app.route('/mint-send-tokens', methods=['POST'])
def mint_tokens():
    data = request.json
    wallet_address = data['wallet_address']
    amount = data['amount']

    sending = mint_and_send_tokens(wallet_address, amount)

    tx_hash = sending["tx_hash"]

    hide_wallet_button = True

    

    return jsonify({
        'ok': True,
        'transaction_hash': tx_hash,
        "hide_wallet_button": hide_wallet_button
    })


"""
@app.route("/subscription", methods=['POST', 'GET'])
def subscription_manifesto():
    return render_template("payment_routes/subscription.html", title="Subscription", CLIENT_ID=CLIENT_ID)

@app.route("/subscription-setup", methods=['POST'])
def activate_subscription():
    data = request.get_json()
    sub_id = data["subscriptionID"]
    print(f"Subscription ID passed: {sub_id}")
    
    unique_azz_id = session.get("unique_azz_id")

    collection.update_one({"unique_azz_id":unique_azz_id}, {"$set":{"subscription_number":sub_id}})

    flash("Congratulations! You have successfully subscribed!")

    return jsonify({"success":True})
"""


@app.route('/payment_buffer/<unique_azz_id>/<id>', methods=['POST', 'GET'])
def payment_buffer(unique_azz_id, id):
    if not id:
        abort(403)  # Forbidden
    
    session['access_granted_payment_result'] = True

    restaurant = collection.find_one({"unique_azz_id":unique_azz_id})

    item_db =  db_items_cache[unique_azz_id].find_one({"id":id})

    if item_db == None:
       abort(403)  # Forbidden
    else:
        items = item_db.get("data")
    print(f"Items on payment buffer: {items}")
    CURRENCY = restaurant.get("res_currency", "USD")

    #checkout_link = session.get("paypal_link")
    if restaurant['addFees']:
        addFees = True
        sum_of_order = sum(float(float(item['amount'])*item['quantity']) for item in items)
        total_to_pay_int = str(sum_of_order+0.45+0.049*sum_of_order)
        total_to_pay = str(round(float(total_to_pay_int), 2))
        fees_amount = round(float(total_to_pay) - sum_of_order,2) 
        print("Add fees on payment buffer")
    else:    
        addFees = False
        total_to_pay = str(sum(float(float(item['amount'])*item['quantity']) for item in items))
        sum_of_order = total_to_pay
        total_to_pay = str(round(float(total_to_pay), 2))
        fees_amount = 0

    session["total"] = total_to_pay
    total_to_pay_display = f"{float(total_to_pay):.2f}"
    session["sum_of_order"] = sum_of_order

    session["unique_azz_id"] = unique_azz_id

    session["items_ordered"] = items
    session['order_id'] = id
    
    return render_template("payment_routes/payment_buffer.html", total_to_pay_display=total_to_pay_display, items=items, total_to_pay=total_to_pay, CLIENT_ID=CLIENT_ID, CURRENCY=CURRENCY, restaurant=restaurant, unique_azz_id=unique_azz_id, addFees=addFees, fees_amount=fees_amount, title="Payment Buffer")


@app.route("/create_payment", methods=['POST','GET'])
def create_payment():
   items = session.get('items_ordered')
   #items = {"items":[{'name':'item1', 'quantity':1, "amount":0.01}, {'name':'item2', 'quantity':2, "amount":0.01}]}

   payment = createPayment(items)
   
   # Check if the payment was successfully created
   if payment['state'] == 'created':
      print(jsonify({'id': payment['id']}))
      return jsonify({'id': payment['id']})
   else:
      return jsonify({'error': 'Payment creation failed'}), 500
   

@app.route("/execute_payment/<unique_azz_id>", methods=['POST','GET'])
def execute_payment(unique_azz_id):
    payment_id = request.args.get('paymentID')
    payer_id = request.args.get('payerID')
    print(f"Payment ID retrieved: {payment_id}")
    print(f"Payer ID retrieved: {payer_id}")
    
    if not payment_id or not payer_id:
        return jsonify({'error': 'Missing paymentID or payerID'}), 400

    exec_success = executePayment(payment_id, payer_id)

    if exec_success:
        return redirect(url_for("success_payment", unique_azz_id=unique_azz_id))
    else:
        return redirect(url_for("cancel_payment", unique_azz_id=unique_azz_id))

@app.route("/create_order", methods=['POST','GET'])
def create_order():
    #addFees = request.args.get('addFees')

    total_to_pay = request.json.get('total_to_pay')

    order = createOrder(total_to_pay=total_to_pay)

    if order.status_code in [201,200]:  # Check if the request was successful
        order_data = order.json()  # Parse the JSON response
        print(f"Order on create_order: {order_data}")
        order_id = order_data['id']
        print(f"Order ID on create_order: {order_id}")
        return jsonify({"id": order_id})
    else:
        print(f"Error creating order: {order.text}")
        return jsonify({"error": "Failed to create order"}), order.status_code

@app.route('/capture_order/<orderID>', methods=['POST'])
def capture_order(orderID):
    top_up_balance = request.args.get("top-up-balance")
    unique_azz_id = request.args.get("unique_azz_id")
    amount = request.args.get('amount', default=0, type=int)
    topped_up_balance = False
    if top_up_balance:
        id_of_who_referred = collection.find_one({'unique_azz_id': unique_azz_id})["id_of_who_referred"]

        result_main = collection.update_one({'unique_azz_id': unique_azz_id}, {"$inc": {"balance": amount}})

        result_add_to_referral = collection.update_one({"referral_code":id_of_who_referred}, {"$inc": {"balance": amount*0.01}})
        
        """
        if result_main.matched_count > 0:
            print("Successfully topped up the balance of the restaurant")
        if result_add_to_referral.matched_count > 1:
            print("Successfully topped up the balance of the REFERRAL restaurant")
        """
        
        flash("You topped up the balance successfully✅")
        
        topped_up_balance = True
    # Now you can use the orderID variable in your function
    print(f"Received orderID: {orderID}")
    captured_order = captureOrder(orderID).json()
    print("Captured Order: ", captured_order)

    if captured_order["status"] == "COMPLETED":
        return jsonify({"captured_order":captured_order, "topped_up_balance_manual":topped_up_balance})
    else:
        return jsonify({"error":True})


@app.route('/assistant_dash', methods=['POST', 'GET'])
def assistant_dashboard_route():
    sub_activated = session.get("subscription_activated")
    unique_azz_id = session.get("unique_azz_id")
    restaurant_name = session.get("restaurant_name")
    qr_code_id = session.get("qr_code_id")
    return render_template("dashboard/assistant_reroute.html", unique_azz_id=unique_azz_id, restaurant_name=restaurant_name, sub_activated=sub_activated, qr_code_id=qr_code_id) 

#######################################################################################################


    
######################### Chat Flow ############################

# Start conversation thread
@app.route('/assistant_start/<assistant_id>', methods=['GET', 'POST'])
def start_conversation(assistant_id):

    #assistant_id = session.get('assistant_id', 'default_assistant_id')  # Default if not provided
    vector_store_id = session.get("menu_vector_id", "vs_HviwnvaEoSsVCltwgc17456Y")
    print(f"Vector store ID on /assistant_start: {vector_store_id}")

    # Create new assistant or load existing
    print("Returned id ", assistant_id) # Debugging line
    print("Starting a new conversation...")  # Debugging line
    thread = CLIENT_OPENAI.beta.threads.create(
    tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
    )                                               
                                                               
    
    # Get current UTC time and format it as dd.mm hh:mm
    # timestamp_utc = datetime.utcnow().strftime('%d.%m.%Y %H:%M')
    # collection_threads.insert_one({"thread_id":thread.id, "restaurant_name":restaurant_name, "timestamp UTC":timestamp_utc})
    
    
    print(f"New thread created with ID: {thread.id}")  # Debugging line
    return jsonify({"thread_id": thread.id, "assistant_id": assistant_id})

@app.route('/assistant_order_chat/<unique_azz_id>')
def assistant_order_chat(unique_azz_id):
    # Retrieve the full assistant_id from the session
    lang = request.args.get('lang', 'en')

    iframe = True if request.args.get("iframe") else False

    res_instance = collection.find_one({"unique_azz_id":unique_azz_id})

    full_assistant_id = res_instance.get("assistant_id")
    restaurant_name = res_instance.get("name")
    restaurant_website_url = res_instance.get("website_url")
    menu_file_id = res_instance.get("menu_file_id")
    menu_vector_id = res_instance.get("menu_vector_id")
    res_currency = res_instance.get("res_currency")
    assistant_turned_on = res_instance.get("assistant_turned_on")
    print(f"Assistant turned on:{assistant_turned_on} of type {type(assistant_turned_on)}")


    start_work = res_instance.get("start_work")
    end_work = res_instance.get("end_work")
    timezone = res_instance.get("timezone")
    if timezone.startswith("Etc/GMT-"):
        timezoneG = timezone.replace("-", "+", 1)
        print("Minus changed")
    elif timezone.startswith("Etc/GMT+"):
        timezoneG = timezone.replace("+", "-", 1)
        print("Plus changed")

    # Get the current date and time in UTC
    now_tz = datetime.now(pytz.timezone(timezoneG))
    current_day = now_tz.weekday()  # Monday is 0 and Sunday is 6
    current_hour = now_tz.hour + now_tz.minute / 60  # Fractional hour

    # Adjust current_day to match our list index where Sunday is 0
    # current_day = (current_day + 1) % 7

    # Check if the current time falls within the working hours
    isWorkingHours = res_instance.get("isOpen")
    print(f"Current time in {timezone}: {now_tz}, Working hours for today: {start_work[current_day]} to {end_work[current_day]}, isWorkingHours: {isWorkingHours}")


    session["unique_azz_id"] = unique_azz_id
    session["full_assistant_id"] = full_assistant_id
    session["menu_file_id"] = menu_file_id
    session["menu_vector_id"] = menu_vector_id
    session["res_currency"] = res_currency
    session["restaurant_name"] = restaurant_name
    # Use the restaurant_name from the URL and the full assistant_id from the session
    return render_template('dashboard/order_chat.html', restaurant_name=restaurant_name, lang=lang, assistant_id=full_assistant_id, unique_azz_id=unique_azz_id, restaurant_website_url=restaurant_website_url, title=f"{restaurant_name}'s Assistant", assistant_turned_on=assistant_turned_on, restaurant=res_instance, iframe=iframe, isWorkingHours=isWorkingHours)



@app.route('/transcribe_voice', methods=['POST'])
def transcribe_voice():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Process audio file
        data = request.form
        language = data.get("language", "en-US")
        print("Language captured: ", language)
        audio_content = file.read()
        print(f"Audio content (length {len(audio_content)} bytes): {audio_content[:100]}...")

         # Call the separate function to convert and transcribe
        # result = convert_and_transcribe_audio_openai(audio_content)
        result = convert_and_transcribe_audio_azure(audio_content, language)
        return jsonify(result)
    except Exception as e:
        print(f"Error during transcription: {e}")
        return jsonify({"error": str(e), "status": "fail"})






@app.route('/generate_response_thread/<unique_azz_id>', methods=['POST'])
def generate_response_thread(unique_azz_id):
    user_message = request.json.get('message', '')
    thread_id = request.json.get('thread_id')
    assistant_id = request.json.get('assistant_id')
    client_id = request.sid
   


    # Get other necessary data
    restaurant_instance = collection.find_one({"unique_azz_id": unique_azz_id})
    menu_file_id = restaurant_instance.get("menu_file_id")
    payment_on = restaurant_instance.get("paymentGatewayTurnedOn")
    html_menu = restaurant_instance.get('html_menu')
    soup = BeautifulSoup(html_menu, 'html.parser')
    rows = soup.find_all('tr')[1:]

    list_of_all_items = []
    list_of_image_links = []
    for row in rows:
        columns = row.find_all('td')
        item = columns[0].text
        ingredients = columns[1].text
        price = columns[2].text
        if columns[3]:
            image_link = columns[3].text
            list_of_image_links.append(image_link)
        tuple_we_deserved = (item, ingredients, f"{price} EUR")
        list_of_all_items.append(tuple_we_deserved)

    # Start the assistant response generation in a separate thread
    clients[client_id]['thread'] = threading.Thread(
        target=get_assistants_response,
        args=(client_id, user_message, thread_id, assistant_id, menu_file_id, client_openai, payment_on, list_of_all_items, list_of_image_links, unique_azz_id)
    )
    clients[client_id]['cancel'] = False
    clients[client_id]['thread'].start()

    return jsonify({"status": "processing"})






@app.route('/generate_voice_output/<unique_azz_id>', methods=["POST", "GET"])
def generate_voice_output(unique_azz_id):
    client = CLIENT_OPENAI
    
    data = request.form
    full_gpts_response = data.get("full_gpts_response")
    language_to_translate_into = data.get("language")

    # list_of_all_items = []
    # list_of_image_links = []

    _, tokens_used = generate_short_voice_output(full_gpts_response, language_to_translate_into)
    
    speech_file_path = Path(__file__).parent / "speech.mp3"

    PRICE_PER_1_TOKEN = 0.0000005
    charge_for_message = PRICE_PER_1_TOKEN * tokens_used
    print(f"Charge for message: {charge_for_message} USD")

    result_charge_for_message = collection.update_one({"unique_azz_id": unique_azz_id}, {"$inc": {"balance": -charge_for_message, "assistant_fund": charge_for_message}})
    if result_charge_for_message.matched_count > 0:
        print("Balances were successfully updated.")
    else:
        print("No matching document found.")

    
    return send_file(
        speech_file_path,
        mimetype='audio/mpeg',
        as_attachment=True,
        download_name='speech.mp3'
    )



@app.route('/generate_response/<unique_azz_id>', methods=['POST', 'GET'])
def generate_response(unique_azz_id):
    # Set the environment variable for Google Cloud credentials
    # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\Users\mmatr\AppData\Roaming\gcloud\application_default_credentials.json'
    

    restaurant_instance = collection.find_one({"unique_azz_id": unique_azz_id})
    payment_on = restaurant_instance.get("paymentGatewayTurnedOn")
    
    # Process text input
    if request.form:
        data = request.form
    elif request.json:
        data = request.json  
    print(f"Data: {data}")  
    user_input = data.get('message', '')
    thread_id = data.get('thread_id')
    assistant_id = data.get('assistant_id')
    language = data.get("language", "en-US")[:2]
    
    print("\n\nlanguage we received on /generate_response: ", language, "\n\n")
    
    transcription = " "


    restaurant_instance = collection.find_one({"unique_azz_id": unique_azz_id})
    menu_file_id = restaurant_instance.get("menu_file_id")
    res_currency = restaurant_instance.get("res_currency")
    print(f"Menu file ID on /generate_response: {menu_file_id}")

    print(f"User input: {user_input}")
    print(f"Thread ID: {thread_id}")
    print(f"Assistant ID: {assistant_id}")

    html_menu = restaurant_instance.get('html_menu')
    soup = BeautifulSoup(html_menu, 'html.parser')
    rows = soup.find_all('tr')[1:]  # Skip the header row

    list_of_all_items = []
    list_of_all_items_names_images = []
    list_of_image_links = []
    for row in rows:
        columns = row.find_all('td')
        item = columns[0].text
        ingredients = columns[1].text
        price = columns[2].text
        if columns[3]:
           image_link = columns[3].text
           list_of_image_links.append(image_link)
        items_image = f'<img src="{image_link} alt="Image of {item}" width="170" height="auto">'
        tuple_we_deserved = (f"Item Name:{item}", f"Item Ingredients:{ingredients}", f"Items Price: {price} EUR", f"Image for {item}: {items_image}")
        #list_of_all_items.append(tuple_we_deserved)
        list_of_all_items.append(tuple_we_deserved)

    # print("List of image links formed: ", list_of_image_links)
    
    #print(f"\n\nList of all items formed: {list_of_all_items}\n\n")  # Debugging line

    print("Thats what we sent to retrieve the gpts response, ", user_input)
    response_llm, tokens_used = get_assistants_response(user_input, language, thread_id, assistant_id, menu_file_id, CLIENT_OPENAI, payment_on, list_of_all_items=list_of_all_items, list_of_image_links=list_of_image_links, unique_azz_id=unique_azz_id)

    PRICE_PER_1_TOKEN = 0.0000005
    charge_for_message = PRICE_PER_1_TOKEN * tokens_used
    print(f"Charge for message: {charge_for_message} USD")

    result_charge_for_message = collection.update_one({"unique_azz_id": unique_azz_id}, {"$inc": {"balance": -charge_for_message, "assistant_fund": charge_for_message}})
    if result_charge_for_message.matched_count > 0:
        print("Balances were successfully updated.")
    else:
        print("No matching document found.")

    print(f"LLM response: {response_llm}")

    for_voice = ""
    '''
    if isinstance(response_llm, Response):
        response_llm_data = response_llm.get_data(as_text=True)
        response_llm_dict = ast.literal_eval(response_llm_data)
        response_llm = response_llm_dict["response"]
    else:
        for_voice = remove_formatted_lines(response_llm)
    
    print(f"For voice: {for_voice}")
    '''
    
    #if "Come to the restaurant and pick up" in response_llm

    # Send the multipart response
    return jsonify({"response_llm":response_llm})





'''
@app.route('/setup_payments', methods=['POST', 'GET'])
def setup_payments():
    restaurant_name = session.get("restaurant_name", "restaurant")
    return render_template("setup_payments.html", title="Payment Setup", restaurant_name=restaurant_name)
'''


@app.route("/change_email", methods=["POST", "GET"])
def change_email():
    unique_azz_id = session.get("unique_azz_id")
    if not unique_azz_id:
        flash("You need to be logged in to change your email.", "error")
        return redirect(url_for('login'))

    if request.method == "POST":
        new_email = request.form.get("new_email")
        if new_email:
            collection.update_one({"unique_azz_id": unique_azz_id}, {"set": {"res_email": new_email}})
            flash("Email updated successfully!", "success")
            return redirect(url_for('profile'))  # Redirect to a profile page or wherever appropriate
        else:
            flash("Please enter a valid email address.", "error")
    
    # GET request
    res_email = collection.find_one({"unique_azz_id": unique_azz_id}).get("res_email")
    return render_template("change_email.html", current_email=res_email)

@app.route("/change_password", methods=["POST", "GET"])
def change_password():
    unique_azz_id = session.get("unique_azz_id")

    res_email = collection.find_one({"unique_azz_id":unique_azz_id}).get("res_email")
    return



@app.route("/thank-you", methods=["GET"])
def thank_you_quick_registration():
    return render_template("start/quick_registered_thanks.html", title="Thank You")





@app.route("/quick_registration", methods=["POST"])
#@auth.login_required
def quick_registration():
    print("Received POST request on '/quick_registration'")
    
    data = request.json
    res_name = data.get("res_name")
    restaurant_url = data.get("restaurant_url", None)
    res_email = data.get("res_email")
    
    print(f"{res_name}, {restaurant_url}, {res_email} - we insert")

    assistant, vector_store_id, menu_file_id = create_assistant(res_name, "EUR", menu_path=None, client=CLIENT_OPENAI, menu_path_is_bool=False)
    
    assistant_id = assistant.id

    quick_reg = {
        "quick_reg": True
    }

    unique_azz_id = res_name.lower().strip().replace(" ", "_").replace("'","")+"_"+assistant_id[-4:]

    password = generate_random_string(10)
    hashed_password = hash_password(password)
    
    insert_restaurant(collection, res_name, unique_azz_id, res_email, hashed_password, restaurant_url, assistant_id, MOM_AI_EXEMPLARY_MENU_FILE_ID, MOM_AI_EXEMPLARY_MENU_VECTOR_ID, "EUR", MOM_AI_EXEMPLARY_MENU_HTML, None, None, None, None, None, logo_id="666af654dee400a1d635eb08", **quick_reg)
    send_confirmation_email_quick_registered(mail, res_email, password, res_name, FROM_EMAIL)

    return jsonify({"success":True, "message":"Restaurant Added Successfully"})

################## Payment routes/Order Posting ###################
@app.route('/no-payment-order-placed/<unique_azz_id>', methods=["POST", "GET"])
def no_payment_order_placed(unique_azz_id):
    if not session.get('access_granted_no_payment_order'):
        abort(403)  # Forbidden
    # Find the instance in MongoDB
    current_restaurant_instance = collection.find_one({"unique_azz_id": unique_azz_id})
    print(f"Restaurant with {unique_azz_id} found: {current_restaurant_instance}")
    
    total_price = session.get("total_price")
    order_id = session.get("order_id")
    items_ordered = session.get("items_ordered")

    restaurant_name = current_restaurant_instance.get("name")
    MEW_ORDER_MESSAGE = f"New order for {restaurant_name.replace('_', ' ')} has been published! 🚀🚀🚀"
    

    # Get current UTC time and format it as dd.mm hh:mm
    # timestamp_utc = datetime.utcnow().strftime('%d.%m.%Y %H:%M')
    return render_template("payment_routes/no_payment_order_finish.html", title="Ready Order", res_unique_azz_id=unique_azz_id, order_id=order_id, total_price=total_price, restaurant_name=restaurant_name.replace('_', ' '), items=items_ordered)




@app.route('/success_payment_backend/<unique_azz_id>', methods=["POST", "GET"])
def success_payment_backend(unique_azz_id):
    suggest_web3_bonus = request.args.get("suggest_web3_bonus")
    
    if suggest_web3_bonus:
        session["suggest_web3_bonus"] = True
    else:
        session["suggest_web3_bonus"] = False

    print("Setup suggest web3 hours in session to ", session["suggest_web3_bonus"])
    
    if not session.get('access_granted_payment_result'):
        abort(403)  # Forbidden

    session.pop('access_granted_payment_buffer', None)
    
    items = session.get('items_ordered')
    total_paid = session.get('total')
    order_id = session.get("order_id")

    sum_of_order = session.get('sum_of_order')

    #total_received = float(round(float(round(float(total_paid),2))*0.99, 2)) # 1 percent retained for prOOOOOOfit
    
    MOM_AI_FEE = float(round(float(round(float(sum_of_order),2))*0.01, 2))+0.10 # 1 percent retained for prOOOOOOfit
    PAYPAL_FEE = 0.35+float(round(float(round(float(sum_of_order),2))*0.0349, 2))

    print(f"MOM AI fee in the order: {MOM_AI_FEE}\n\n")
    print(f"PAYPAL fee in the order: {PAYPAL_FEE}\n\n")

    total_received = float(total_paid) - float(round(MOM_AI_FEE, 2)) - float(round(PAYPAL_FEE, 2))

    print(f"That's how much customer paid: {total_paid}")
    print(f"That's how much restaurant received: {total_received}")

    # Find the instance in MongoDB
    current_restaurant_instance = collection.find_one({"unique_azz_id": unique_azz_id})
    print(f"Restaurant with {unique_azz_id} found: {current_restaurant_instance}")

    # Get current UTC time and format it as dd.mm hh:mm
    timestamp_utc = datetime.utcnow().strftime('%d.%m.%Y %H:%M')

    # Create Item instances for each item in the request
    #items = [Item(name=item['name'], quantity=item['quantity']) for item in items_data]
    
    assistant_used = session["unique_azz_id"]
    
    order_to_pass = {"items":[{'name':item['name'], 'quantity':item['quantity']} for item in items], 
                        "orderID":order_id,
                        "timestamp": timestamp_utc,
                        "total_paid": total_paid,
                        "mom_ai_restaurant_assistant_fee": float(round(MOM_AI_FEE, 2)),
                        "paypal_fee": float(round(PAYPAL_FEE, 2)),
                        "paid":"PAID",
                        "published":True}
    
    order_dashboard_id = assistant_used

    db_order_dashboard[order_dashboard_id].insert_one(order_to_pass)

    all_ids_for_acc = current_restaurant_instance.get('notif_destin')

    if all_ids_for_acc is not None:
        for chatId in all_ids_for_acc:
            send_telegram_notification(chat_id=chatId, message=MEW_ORDER_MESSAGE)


    current_balance = current_restaurant_instance.get("balance")
    print(f"Current balance before updating: {current_balance}")

    if len(list(db_order_dashboard[order_dashboard_id].find())) == 1: 
        result = collection.update_one({'unique_azz_id': unique_azz_id}, {"$inc": {"balance": total_received-3}})
        print("Deducted initial 3 Euros")
    else:
        result = collection.update_one({'unique_azz_id': unique_azz_id}, {"$inc": {"balance": total_received}})

    all_ids_for_acc = current_restaurant_instance.get('notif_destin')

    restaurant_name = current_restaurant_instance.get("name")
    MEW_ORDER_MESSAGE = f"New order for {restaurant_name.replace('_', ' ')} has been published! 🚀🚀🚀"
    
    if all_ids_for_acc is not None:
        for chatId in all_ids_for_acc:
            send_telegram_notification(chat_id=chatId, message=MEW_ORDER_MESSAGE)
    
    # Check if the update was successful
    if result.matched_count > 0:
        print("Added funds for the order successfully.")
    else:
        print("No matching document found.")

    current_balance = current_restaurant_instance.get("balance")
    print(f"Current balance after updating: {current_balance}")

    print(f"Items: {items} on success payment route")
    print(f"Total paid: {total_paid} on success payment route")


    flash("Your Order was Successfully Placed!")

    # This route can be used for further processing if needed
    return redirect(url_for('success_payment_display', unique_azz_id=unique_azz_id, id=order_id))



@app.route('/success_payment/<unique_azz_id>/<id>', methods=["GET", "POST"])
def success_payment_display(unique_azz_id, id):
    suggest_web3_bonus = session.get("suggest_web3_bonus", False)

    print("Suggest web3 bonus, ", suggest_web3_bonus)
    
    if not id:
        abort(403)
    current_restaurant_instance = collection.find_one({"unique_azz_id": unique_azz_id})
    restaurant_name = current_restaurant_instance.get("name")
    result = db_items_cache[unique_azz_id].delete_one({"id":id})

    order = db_order_dashboard[unique_azz_id].find_one({"orderID": id})

    items = order.get("items")

    total_paid = session.get('total')

    # Check if the delete was successful
    if result.deleted_count > 0:
        print("Document deleted.")
    else:
        print("No document matches the query. Nothing was deleted.")

    if session.get("suggest_web3_bonus", None):
        session.pop("suggest_web3_bonus")

    return render_template('payment_routes/success_payment.html', title="Payment Successful", restaurant_name=restaurant_name, 
                           res_unique_azz_id=unique_azz_id, 
                           order_id=id, 
                           suggest_web3_bonus=suggest_web3_bonus, 
                           items=items,
                           total_paid=total_paid)
    

@app.route('/cancel_payment/<unique_azz_id>')
def cancel_payment(unique_azz_id):

    if not session.get('access_granted_payment_result'):
        abort(403)  # Forbidden

    session.pop('access_granted_payment_buffer', None)
    restaurant_name = session.get("restaurant_name", "restaurant_placeholder")
    
    id = session['order_id']

    result = db_items_cache[unique_azz_id].delete_one({"id":id})

    # Check if the delete was successful
    if result.deleted_count > 0:
        print("Document deleted.")
    else:
        print("No document matches the query. Nothing was deleted.")
    
    res_unique_azz_id = session.get("unique_azz_id")
    
    # This route can be used for further processing if needed
    return render_template('payment_routes/cancel_payment.html', title="Payment Canceled", restaurant_name=restaurant_name, res_unique_azz_id=res_unique_azz_id)


@app.route('/withdraw-funds', methods=['POST', 'GET'])
def request_withdraw_funds():
    available_amount = round(session.get("current_balance"), 2)
    return render_template("payment_routes/withdraw/request_withdrawal.html", title="Withdraw Funds", available_amount = available_amount)


@app.route('/post-withdrawal-request', methods=['POST', 'GET'])
def post_withdrawal_request():
    # Retrieve the withdrawal description from the form data
    withdrawal_description = request.form.get('withdrawal_description')
    
    res_email = session.get('restaurant_email')
    res_name = session.get('restaurant_name')
    withdraw_amount = round(session.get("current_balance"), 2)

    send_confirmation_email_request_withdrawal(mail, res_email, res_name, withdraw_amount, withdrawal_description, FROM_EMAIL)
    current_restaurant_instance = collection.find_one({"email": res_email})
    
    if current_restaurant_instance.get("await_withdrawal"):
        print("Chose IF")
        result_withdraw_request = collection.update_one({"email":res_email}, {"$set": {"balance": 0}, "$inc": {"await_withdrawal": withdraw_amount}})
    else:
        print("Chose ELSE")
        result_withdraw_request = collection.update_one({"email":res_email}, {"$set": {"balance": 0, "await_withdrawal": withdraw_amount}})
    # Check if the update was successful
    if result_withdraw_request.matched_count > 0:
        print("Balance decreased successfully in request withdraw route.")
    else:
        print("No matching document found.")

    return render_template("payment_routes/withdraw/withdrawal_posted.html", title="Withdrawal Requested", withdraw_amount=withdraw_amount, res_email=res_email)


"""
@app.route('/withdraw-funds-auto', methods=['POST', 'GET'])
def pp_or_web3_withdraw_display():
    return render_template("payment_routes/withdraw/main_withdraw.html", title="Withdraw Funds")

@app.route('/withdraw-funds-paypal-post', methods=['POST', 'GET'])
def pp_withdraw_funds():
    email = request.form['email']
    amount_usd = session.get("current_balance")  # Specify the amount to send
    response = send_payout_pp(email, amount_usd)
    return response  # You might want to handle the response appropriately
"""






###########################################




################################## Order Display #################################

@app.route('/view_orders', methods=['GET'])
def view_orders():
    restaurant_name = session.get("restaurant_name")
    return render_template('orders_dashboard/orders_display.html', restaurant_name=restaurant_name)




@app.route('/view_orders_ajax', methods=['GET'])
def view_orders_ajax():
    #restaurant_name = session.get("restaurant_name")
    #restaurant_email = session.get("restaurant_email")
    unique_azz_id = session.get("unique_azz_id")
    
    order_dashboard_id = unique_azz_id

    order_collection = db_order_dashboard[order_dashboard_id]

    # Query all orders from the database
    orders = list(order_collection.find())

    # Format orders for display
    orders_list = []
    for order in orders:
        order_info = {
            'foods': [item for item in order['items']],
            'timestamp': order['timestamp'],
            'published': order['published'],
            'orderID':order.get('orderID', 'no ID provided'),
            'paid':order.get('paid')

        }
        orders_list.append(order_info)

    return jsonify({'orders': orders_list})









"""
@app.route('/orders', methods=['GET', 'POST'])
def add_order_record():
    if request.method == 'POST':
        data = request.json
        print("POST order on orders endpoint: ", data)
        items_data = data.get('items', [])  # Default to an empty list if not provided
        
        # Get current UTC time and format it as dd.mm hh:mm
        timestamp_utc = datetime.utcnow().strftime('%d.%m %H:%M')

        # Create Item instances for each item in the request
        #items = [Item(name=item['name'], quantity=item['quantity']) for item in items_data]
        
        order_to_pass = {"items":[{'name':item['name'], 'quantity':item['quantity']} for item in items_data], 
                         "timestamp": timestamp_utc,
                         "published":False}
        
        print(order_to_pass, "\n\n\n\n")

        
        restaurant_name = session["restaurant_name"]
        order_collection = db_order_dashboard[restaurant_name]

        db_order_dashboard[restaurant_name].insert_one(order_to_pass)
        
        order_collection.update_one({'_id': document_to_post['_id']}, {'$set': {'published': True}})
        
        if 'items' in data:
            # Save the order to the selected collection and keep the reference
            order_collection.insert_one(order_to_pass)  # Assuming Order has a to_mongo method       
            last_inserted_document = order_collection.find().sort('_id', -1).limit(1)
            # Since `find` returns a cursor, we convert it to a list to access the document
            # If there is a document, it will be the first in the list
            if last_inserted_document:
                document_to_post = list(last_inserted_document)[0]
                print(document_to_post)
                # Update the 'published' attribute of the fetched document to True
                result = order_collection.update_one({'_id': document_to_post['_id']}, {'$set': {'published': True}})

                # Check if the update was successful
                if result.matched_count > 0:
                    send_telegram_notification()
                    print("Document updated successfully. Published set to True.")
                    return "Document updated successfully. Published set to True."
                else:
                    print("Document not found for update.")
                    return "Document not found for update."
        return jsonify({"response":"Order Successfully Posted with \"published:False\"!"})

    elif request.method == 'GET':
        # For a GET request, return a simple message
        return 'Send a POST request to submit an order.' 
"""



################################### Guides/Static Pages ####################################

@app.route('/excel_guide', methods=['GET'])
def serve_excel_guide():
    return render_template("guides/excel_guide.html", title="Menu Forming Guide", restaurant_name="MOM AI Assistant")

@app.route('/privacy-policy', methods=['GET'])
def serve_privacy_policy():
    return render_template("privacy_policy/privacy_policy.html", title="Privacy Policy", restaurant_name="MOM AI Assistant")

######### Profile of the restaurant ##############
@app.route('/restaurant/<unique_azz_id>', methods=['GET'])
def show_restaurant_profile_public(unique_azz_id):
    restaurant = collection.find_one({"unique_azz_id":unique_azz_id})
    res_coords = ast.literal_eval(restaurant["location_coord"])
    latitude = res_coords["lat"]
    longitude = res_coords["lng"]

    html_menu = restaurant.get("html_menu")
    if html_menu:
        wrapped_html_table = wrap_images_in_html_table(html_menu)

    restaurant_reviews = db_rest_reviews[unique_azz_id]
    
    reviews = restaurant_reviews.find()

    reviews = list(reviews)

    print("Reviews passed: ", reviews)

    there_are_reviews = True if len(reviews)>=1 else False
    
    start_work = restaurant.get("start_work")
    end_work = restaurant.get("end_work")
    timezone = restaurant.get("timezone")
    if timezone.startswith("Etc/GMT-"):
        timezoneG = timezone.replace("-", "+", 1)
        print("Minus changed")
    elif timezone.startswith("Etc/GMT+"):
        timezoneG = timezone.replace("+", "-", 1)
        print("Plus changed")

    # Get the current date and time in UTC
    now_tz = datetime.now(pytz.timezone(timezoneG))
    current_day = now_tz.weekday()  # Monday is 0 and Sunday is 6
    current_hour = now_tz.hour + now_tz.minute / 60  # Fractional hour

    # Adjust current_day to match our list index where Sunday is 0
    # current_day = (current_day + 1) % 7

    start_working_hours = [convert_hours_to_time(hour) for hour in restaurant["start_work"]]
    end_working_hours = [convert_hours_to_time(hour) for hour in restaurant["end_work"]]

    # Check if the current time falls within the working hours
    isWorkingHours = start_work[current_day] <= current_hour < end_work[current_day]

    return render_template("marketing_dashboard/public_profile.html", restaurant=restaurant, 
                           title=restaurant.get("name", "AI Restaurant"), 
                           GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY, 
                           latitude=latitude, longitude=longitude, 
                           isWorkingHours=isWorkingHours,
                           start_working_hours=start_working_hours,
                           end_working_hours=end_working_hours,
                           unique_azz_id=unique_azz_id,
                           html_menu=wrapped_html_table,
                           reviews=reviews,
                           there_are_reviews=there_are_reviews)

    
if __name__ == '__main__':
    app.run(debug=True)




    
"""
@app.route('/trigger_binance_withdrawal/<web3_wallet_address>/<total_amount>', methods=['POST', 'GET'])
def trigger_binance_withdrawal(total_amount, web3_wallet_address):
    success_withdrawing = completion_on_binance_web3_wallet_withdraw(total_amount, web3_wallet_address)
    if success_withdrawing:
        return f"99% of {total_amount} was sent to {web3_wallet_address} successfully"
    else: 
        return f"Error sending {total_amount} USDT to the restaurant\'s wallet: {web3_wallet_address}"

"""


"""

@app.route('/assistant', methods=['POST', 'GET'])
def assistant_display():
    data = request.form
    print(data)
    user_message = data.get('user_message')
    messages = session.get('messages', [])
    if user_message:
        messages.append({'sender': 'user', 'content': user_message})
        messages.append({'sender': 'assistant', 'content': "LLM response"})
    session['messages'] = messages

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return only the messages part for AJAX requests
        html = render_template_string('''
        {% for message in messages %}
            <div style="{{ 'background-color: #000; color: white;' if message.sender == 'assistant' else 'background-color: #e5e5e5;' }} margin: 10px; padding: 10px; text-align: {{ 'right' if message.sender == 'assistant' else 'left' }}; border-radius: 10px;">
                {{ message.content }}
            </div>
        {% endfor %}
        ''', messages=messages)
        return html
    return render_template("assistant_chat.html", messages=messages)

@app.route('/create_stellar_account', methods=['POST'])
def create_stellar_payments():
    # Get the form data
    # circle_api_key = request.form['circleApiKey']
    stellar_private_key = request.form['stellarSecretKey']
    stellar_public_key = request.form['stellarPublicKey']
    
    stellar_acc = create_stellar_account(stellar_private_key, stellar_public_key)

    restaurant_name = session.get("restaurant_name", "Matronin's")
    menu_encoded = session.get("restaurant_name", "Matronin's menu")
    script_encoded = session.get("restaurant_name", "Matronin's script")
    assistant_id = session.get("restaurant_name", "Matronin's assistant")
    email = session.get("restaurant_name", "Matronin's email")
    password = session.get("restaurant_name", "Matronin's password")

    # register the restaurant in db
    insert_document(collection, restaurant_name, email, password, assistant_id, stellar_public_key, stellar_private_key)
 
    return render_template("register_finish.html")

"""


""" Withdraw funds hyperwallet leagcy code

# Route to render the registration form
@app.route('/register-withdrawal-account', methods=['GET'])
def register_account():
    restaurant_email = session.get("restaurant_email")
    return render_template("payment_routes/withdraw/register_hyperwallet.html", title="Register Withdrawal Account", restaurant_email=restaurant_email)

@app.route('/send-payout', methods=['POST'])
def send_payout():
    data = request.json
    print(f"Received data: {data}")  # Debugging line

    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    amount = data['amount']
    addressLine = data['addressLine']
    city = data['city']
    stateProvince = data['stateProvince']
    country = data['country']
    postalCode = data['postalCode']
    bank_account_number = data['bank_account_number']
    routing_number = data['routing_number']

    print(f"Creating user with: {first_name} {last_name}, {email}, {addressLine}, {city}, {stateProvince}, {country}, {postalCode}")  # Debugging line
    user_response = create_user(first_name, last_name, email, addressLine, city, stateProvince, country, postalCode)
    print(f"User response: {user_response}")  # Debugging line

    user_token = user_response.get('token')
    print(f"User token: {user_token}")  # Debugging line

    bank_account_details = {
        "transferMethodCountry": "US",
        "transferMethodCurrency": "USD",
        "type": "BANK_ACCOUNT",
        "bankAccountPurpose": "CHECKING",
        "branchId": routing_number,
        "bankAccountId": bank_account_number,
        "bankAccountHolderName": f"{first_name} {last_name}"
    }

    print(f"Creating bank account with details: {bank_account_details}")  # Debugging line
    bank_account_response = create_bank_account(user_token, bank_account_details)
    print(f"Bank account response: {bank_account_response}")  # Debugging line

    print(f"Making payment of {amount} to user token {user_token}")  # Debugging line
    payment_response = make_payment(user_token, amount)
    print(f"Payment response: {payment_response}")  # Debugging line

    if 'errors' not in payment_response:
        print("Payout sent successfully")  # Debugging line
        return jsonify(success=True, message="Payout sent successfully", data=payment_response)
    else:
        print("Error sending payout")  # Debugging line
        return jsonify(success=False, message="Error sending payout", data=payment_response)

# Route to handle form submission
@app.route('/register-withdrawal-account-post', methods=['POST'])
def register_account_submit():
    data = request.json
    print(f"Received data: {data}")  # Debugging line

    # Extract user information
    first_name = data['first_name']
    last_name = data['last_name']
    email = data["email"]
    addressLine = data['addressLine']
    city = data['city']
    stateProvince = data['stateProvince']
    country = data['country']
    postalCode = data['postalCode']

    # Create user
    print(f"Creating user with: {first_name} {last_name}, {email}, {addressLine}, {city}, {stateProvince}, {country}, {postalCode}")  # Debugging line
    user_response = create_user(first_name, last_name, email, addressLine, city, stateProvince, country, postalCode)
    print(f"User response: {user_response}")  # Debugging line

    if 'token' not in user_response:
        return jsonify(success=False, message="Error creating user", data=user_response)

    user_token = user_response['token']
    print(f"User token: {user_token}")  # Debugging line

    # Extract bank account information
    swift_id = data['swift_id']
    iban_id = data['iban_id']
    bank_address = data['bank_address']
    bank_city = data['bank_city']

    # Create bank account
    print(f"Creating bank account with details: {swift_id}, {iban_id}, {bank_address}, {bank_city}")  # Debugging line
    bank_account_response = create_bank_account(user_token, swift_id, iban_id, bank_address, bank_city)
    print(f"Bank account response: {bank_account_response}")  # Debugging line
    
    user_bank_token = bank_account_response.get('token')

    collection.update_one({'email': email}, {'$set': {'withdrawal_account_token': user_token, 'user_bank_token': user_bank_token}})
    print(f"\nAdded user token and bank token to the user with email {email} successfully\n")  # Debugging line

    if 'errors' not in bank_account_response:
        print("Bank account created successfully")  # Debugging line
        return jsonify(success=True, message="Bank account created successfully", data=bank_account_response)
    else:
        print("Error creating bank account")  # Debugging line
        return jsonify(success=False, message="Error creating bank account", data=bank_account_response)


@app.route('/withdraw_funds', methods=['POST', 'GET'])
def withdraw_funds():
    restaurant_email = session.get("restaurant_email")
    user = collection.find_one({'email': restaurant_email})
    print(user)
    funds_available = user.get("balance")

    if "withdrawal_account_token" in user.keys():
        return render_template("payment_routes/withdraw/withdraw_hyperwallet_form.html", title="Withdraw Funds", withdrawal_account_token=user["withdrawal_account_token"])
        #return redirect(url_for("withdraw_funds_form"))
    else:
        return render_template("payment_routes/withdraw/register_hyperwallet.html", title="Register Withdraw Funds", funds_available=funds_available, restaurant_email=restaurant_email)


"""