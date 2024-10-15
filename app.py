from flask import Flask, abort, make_response, jsonify, request, render_template, session, redirect, url_for, flash, render_template_string, Response, send_file, stream_with_context
#from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from werkzeug.utils import secure_filename
import statistics
from flask_migrate import Migrate
import os
from bland.twilio_stuff import full_get_insert_twilio_number
import threading
import glob
from urllib.parse import urlparse
# from google.cloud import speech
import qrcode
from geopy.distance import geodesic
import bcrypt
import secrets
#from io import BytesIO
#from flask_socketio import SocketIO, disconnect
import gridfs
from pydub import AudioSegment
import uuid
import re
import pandas as pd
import base64
from bs4 import BeautifulSoup
from google_folder.google_cloud_storage import delete_file_by_url_google, upload_file_google, download_file_google, list_files_google, upload_file_bytes_google
import markdown
import json
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
#from pyrogram import filters
#from utils.telegram import app_tg
from bland.functions import get_data_for_pathway_change, get_call_length_and_phone_number, update_phone_number_non_english, update_phone_number, insert_the_nodes_and_edges_in_new_pathway, create_the_suitable_pathway_script, buy_and_update_phone, pathway_serving_a_to_z_initial, pathway_proper_update, send_the_call_on_number_demo, create_the_suitable_pathway_script
from utils.forms import ResetPasswordForm, ChangeCredentialsForm, RestaurantForm, UpdateMenuForm, ConfirmationForm, LoginForm, RestaurantFormUpdate, ProfileForm 
from functions_to_use import generate_short_voice_output_streaming, update_menu_on_openai, delete_file_from_s3, upload_file_to_s3, get_assistants_response_celery_VOICE_ONLY_streaming, generate_short_voice_output_VOICE_ONLY, fully_extract_menu_from_image_celery, s3, generate_ai_item_description, generate_ai_menu_item_image, generate_ai_menu_item_image_celery, create_talk_video, get_talk_video, create_and_get_talk_video, full_intro_in_momai_google, FROM_EMAIL, app, socketio, cache, mail, turn_assistant_off_low_balance, send_email_raw, mint_and_send_tokens, convert_and_transcribe_audio_azure, convert_and_transcribe_audio_openai, send_confirmation_email_quick_registered, generate_random_string, generate_short_voice_output, get_post_filenames, get_post_content_and_headline, InvalidMenuFormatError, CONTRACT_ABI, generate_qr_code_and_upload, remove_formatted_lines, convert_hours_to_time, setup_working_hours, hash_password, check_password, clear_collection, upload_new_menu, convert_xlsx_to_txt_and_menu_html, create_assistant, insert_restaurant, get_assistants_response, send_confirmation_email, generate_code, check_credentials, send_telegram_notification, send_confirmation_email_request_withdrawal, send_waitlist_email, send_confirmation_email_registered, convert_webm_to_wav, MOM_AI_EXEMPLARY_MENU_HTML, MOM_AI_EXEMPLARY_MENU_FILE_ID, MOM_AI_EXEMPLARY_MENU_VECTOR_ID, get_assistants_response_celery, celery 
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
from google.oauth2 import id_token
from google.auth.transport import requests

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
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL_CORRECT')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

if not os.environ.get("LOCAL_DEV") == "True":
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)

    # Define the Post model
    class Post(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        url_slug = db.Column(db.String(150), nullable=True, unique=True, index=True)
        title = db.Column(db.String(100), nullable=False)
        content = db.Column(db.Text, nullable=False)
        image_url = db.Column(db.String(2048), nullable=True)  # New column for image URL
        created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    DROP_THE_EXISTING_TABLES = os.environ.get("DROP_THE_EXISTING_TABLES", "False") == "True"
    
    # Ensure the tables are created
    with app.app_context():
        if DROP_THE_EXISTING_TABLES:
            db.drop_all()
            print("Dropped the tables")
        db.create_all()

# oauth = OAuth(app)

GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_OAUTH_CLIENT_REDIRECT_URI = os.environ.get("GOOGLE_OAUTH_CLIENT_REDIRECT_URI", 'http://localhost:5000/login/callback')

"""
# Configuration for Google OAuth
google = oauth.register(
    name='google',
    client_id=GOOGLE_OAUTH_CLIENT_ID,
    client_secret=GOOGLE_OAUTH_CLIENT_SECRET,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    redirect_uri=GOOGLE_OAUTH_CLIENT_REDIRECT_URI,
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
    client_kwargs={'scope': 'email'}  # Disable state validation (not recommended for production)
)
"""





CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID") if os.environ.get("PAYPAL_SANDBOX") == "True" else os.environ.get("PAYPAL_LIVE_CLIENT_ID")
SECRET_KEY = os.environ.get("PAYPAL_SECRET_KEY") if os.environ.get("PAYPAL_SANDBOX") == "True" else os.environ.get("PAYPAL_LIVE_SECRET_KEY")

PRICE_PER_1_TOKEN = 0.0000005

MOM_AI_EXEMPLARY_MENU_VECTOR_ID = "vs_fszfiVR3qO7DDHNSkTQn8fYH"
MOM_AI_EXEMPLARY_MENU_FILE_ID = "file-FON6GkHWdj1c4xioGCpje05N"

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app.config.from_object(Config)




if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.mkdir(app.config['UPLOAD_FOLDER'])

mongodb_connection_string = os.environ.get("MONGODB_CONNECTION_URI", "mongodb://localhost:27017")

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

PRICE_OF_MINUTE_PHONE_CALL = 0.15

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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

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
    flash("Internal Server Error Occurred - you were redirected to the error page")
    return render_template("errors/500_error_template.html", title="Error 500"), 500



def charge_for_ai_phone_number():
    # Get today's date
    today = datetime.today()
    formatted_date_today = today.strftime('%Y-%m-%d')

    # Extract the day number
    day_number = today.day

    today_day = day_number

    if day_number > 28:
        today_day = 28
    
    for res_instance in list(collection.find()):
        
        start_ai_phone_number = res_instance.get("ai_phone_number")
        
        if start_ai_phone_number:
            date_of_sub = res_instance.get("ai_subscription_date")

            date_format = "%Y-%m-%d"

            # Parsing the date
            parsed_date_of_sub = datetime.strptime(date_of_sub, date_format)

            if parsed_date_of_sub.day == today_day and not formatted_date_today == parsed_date_of_sub:
                unique_azz_id = res_instance.get("unique_azz_id")
                if res_instance.get("balance") > 23:
                    collection.update_one({"unique_azz_id": unique_azz_id}, {"$inc":{"balance": -20}})
                    # print(f"Deducted 20 Euros from account of {res_instance.get('email')}")
                else:
                    message_html = f'<p>Bruv, top up {res_instance.get("name")}\'s balance to keep benefitting from autopilot phone orders'
                    send_email_raw(mail, res_instance.get("email"), message_html, f"URGENT! {res_instance.get('name')}'s AI phone assistant continuation failed! You can lose automated phone order taking!", FROM_EMAIL)
                    # print(f"Sent Warning email on {res_instance.get('email')}")

        # print(f"Skimmed through {res_instance.get('name')}")



def schedule_tasks():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=clear_collection, trigger="interval", minutes=15)
    scheduler.add_job(func=setup_working_hours, trigger="interval", seconds=10)
    scheduler.add_job(func=turn_assistant_off_low_balance, trigger="interval", seconds=15)
    # Run once per day at 12:00 PM
    scheduler.add_job(func=charge_for_ai_phone_number, trigger="cron", hour=12, minute=0)
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


@app.route('/google_login')
def google_login():
    # Generate a nonce and store it in the session
    nonce = secrets.token_urlsafe(16)
    session['nonce'] = nonce
    redirect_uri = url_for('authorized', _external=True)
    print(f"Generated state: {session.get('_state_')}")
    return google.authorize_redirect(redirect_uri, nonce=nonce)

@app.route('/login/callback')
def authorized():
    print(f"Returned state: {request.args.get('state')}")
    # Retrieve the nonce from the session
    nonce = session.get('nonce')
    token = google.authorize_access_token()
    if not token:
        return 'Access denied: could not fetch token'
    
    user_info = google.parse_id_token(token, nonce=nonce)

    session["email"] = user_info['email']
    
    return 'Logged in as: ' + user_info['email']

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

    if request.args.get("no_google_login") == "True":
        flash("No MOM AI Restaurant account is conected to this Google Profile - Please, register.")

    form = RestaurantForm()
    print("Form Created")

    if form.validate_on_submit():
        print("Pressed submit")

        session["email"] = form.email.data
        session["password"] = form.password.data

        if check_credentials(form.email.data, form.password.data, collection, for_login_redirect=True):
            flash('It seems that your email and password are already registered. Please log in.')
            return redirect(url_for('login'))

        # restaurant_name = form.restaurant_name.data
        # print(f"Restaurant name: {restaurant_name}")

        # if form.restaurant_url.data:
            # restaurant_url = form.restaurant_url.data
            # print(f"Restaurant website URL: {restaurant_url}")
        # else:
            # restaurant_url = "No URL provided"

        #other_instructions = form.other_instructions.data
        #print(f"Other instructions: {other_instructions}")

        password = form.password.data
        #print(f"Restaurant password: {password}")

        # location_coord = request.form['location']
        # print(f"Location: {location_coord}")
        
        # location_name = request.form['locationName']
        # print(f"Location Name: {location_name}")

        # session["location_coord"] = location_coord
        # session["location_name"] = location_name

        #currency = form.currency.data
        #print(f"Currency of the restaurant: {currency}")

        currency = "EUR"

        session["currency"] = "EUR"

        # Save the image to GridFS
        # image = form.image.data
        #print(f'Image Received:{image}')
        # if image:
            # filename = secure_filename(image.filename)
            # file_id = fs.put(image, filename=filename)
            # print(f'Raw file id {file_id} and string file id {str(file_id)}')
            # session["logo_id"] = str(file_id)
        
        # if form.referral_id.data:
            # session["id_of_who_referred"] = form.referral_id.data
        
        # session["custom_menu_provided"] = False
        """
        if request.files.get('menu'):
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
            
            menu_txt_path, html_menu_tuples = convert_xlsx_to_txt_and_menu_html(menu_xlsx_path, menu_save_path, currency)
            
            html_menu = html_menu_tuples
            
            if not isinstance(menu_txt_path, str):
               print("Entered Invalid Menu Error.")
               flash(str(menu_txt_path))
               return redirect("/register")
            # print(f"Generated menu txt file: {menu_txt_path}")

            session["restaurant_name"] = restaurant_name
            session["res_website_url"] = restaurant_url
            session["html_menu"] = html_menu   
            session["custom_menu_provided"] = True    

            with open(menu_txt_path, 'rb') as menu_file:
                menu_encoded = base64.b64encode(menu_file.read())
                #script_encoded = base64.b64encode(script_file.read())
        
            #session["menu_encoded"] = menu_encoded
            #session["script_encoded"] = script_encoded

            print(f"\nMenu encoded: {menu_encoded}\n")
            #print(f"\nScript encoded: {script_encoded}\n")
            print("Files encoded")
            
            print(f"Menu TXT path passed {menu_txt_path}")

            # assistant, menu_vector_id, menu_file_id = create_assistant(restaurant_name, currency, menu_txt_path, client=CLIENT_OPENAI)

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

        """
        
        session["password"] = password


        # session["restaurant_name"] = restaurant_name
        # session["res_website_url"] = restaurant_url        

        
        session["password"] = password

        #print(f"Files saved at {menu_txt_path} and {script_path}")
        
        #session["menu_encoded"] = menu_encoded
        #session["script_encoded"] = script_encoded

        # assistant, menu_vector_id, menu_file_id = create_assistant(restaurant_name, currency, menu_path=None, client=CLIENT_OPENAI, menu_path_is_bool=False)
        # session['assistant_id'] = assistant.id
        # session['menu_vector_id'] = menu_vector_id
        # session['menu_file_id'] = menu_file_id

        # unique_azz_id = restaurant_name.lower().strip().replace(" ", "_").replace("'","")+"_"+assistant.id[-4:]
        # session["unique_azz_id"] = unique_azz_id
        
        print("We are right before qr code generation")

        # session["qr_code_id"] = qr_code_id

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
                flash(f"Error in field '{field}': {error}", "danger")
                if "csrf" in error.lower():
                    flash(f"Error in field '{field}': {error} - PLEASE, RELOAD THE PAGE!", 'danger')
        print("Form not submitted or validation failed")
    return render_template('start/register.html', 
                           form=form, title="Register", 
                           GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY,
                           GOOGLE_OAUTH_CLIENT_ID=GOOGLE_OAUTH_CLIENT_ID)

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
            flash('You have been successfully logged in!', "success")
            return redirect(url_for('dashboard_display'))
        else:
            print('Login failed. Check your email and password.')
            flash('Login failed. Check your email and password.')
            return redirect(url_for('login'))
    return render_template('start/login.html', form=form, title="Login", 
                           GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY,
                           GOOGLE_OAUTH_CLIENT_ID=GOOGLE_OAUTH_CLIENT_ID)

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
    image_url = post.image_url
    return render_template('blog-posts/post.html', content=content, title=title, created_at=created_at, image_url=image_url)

                           

@app.route('/all_posts')
def all_posts():
    page = request.args.get('page', 1, type=int)

    # Get the total count of all posts
    total_posts_count = Post.query.count()

    posts_pagination = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=10)
    posts = posts_pagination.items

    print(len(posts))
    
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
            'link': None,  # Initialize with None
            'created_at': post.created_at.strftime('%d.%m.%Y %H:%M'),  # Format the created_at field
            'image_url': post.image_url
        })

        # Attempt to set the 'link', fallback to default if url_for fails
        try:
            post_data[-1]['link'] = url_for('post', url_slug=post.url_slug)
        except Exception:
            post_data[-1]['link'] = '#'  # Assign a default link in case of failure
    
    next_url = url_for('all_posts', page=posts_pagination.next_num) if posts_pagination.has_next else None
    prev_url = url_for('all_posts', page=posts_pagination.prev_num) if posts_pagination.has_prev else None

    print(next_url)
    print(prev_url)
    
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
                flash('Invalid confirmation code. Please try again.', 'danger')

    return render_template('email_confirm/enter_code.html', form=form, res_email=res_email, title="Enter Confirmation Code")



@app.route('/confirm_email/<res_email>')
def confirm_email(res_email):
    # Check if the session variable is set
    if not session.get('access_granted_email_confirm_page'):
        abort(403)  # Forbidden
    
    # Clear the session variable after access
    session.pop('access_granted_email_confirm_page', None)

    #session["res_email"] = session.get("verified_res_email")

    res_name = session.get("restaurant_name", "name_default")
    # print(f"Restaurant Name: {res_name}")

    #menu_file = session.get("menu_encoded", "menu_placeholder")
    #print(f"Menu File: {menu_file}")

    #script_file = session.get("script_encoded", "script_placeholder")
    #print(f"Script File: {script_file}")

    assistant_id = session.get("assistant_id", "assistant_id_placeholder")
    # print(f"Assistant ID: {assistant_id}")

    res_password = session.get("password", None)
    # print(f"Restaurant Password: {res_password}")

    #verified_res_email = session.get("verified_res_email", "email_placeholder")

    restaurant_name = session.get("restaurant_name")
    
    website_url = session.get("res_website_url", "Restaurant URL placeholder")

    menu_file_id = session.get("menu_file_id")
    menu_vector_id = session.get("menu_vector_id")

    currency = session.get("currency")
    if session.get("custom_menu_provided"):
        html_menu = session.get("html_menu", MOM_AI_EXEMPLARY_MENU_HTML)
    else:
        html_menu = MOM_AI_EXEMPLARY_MENU_HTML

    file_id = session.get("logo_id", "666af654dee400a1d635eb08")

    qr_code_id = session.get("qr_code_id")

    hashed_res_password = hash_password(res_password)

    session["hashed_res_passord"] = hashed_res_password

    # location_coord = session["location_coord"]
    # location_name = session["location_name"]

    # unique_azz_id = session.get("unique_azz_id")
    # print("Unique azz id we insert, ", unique_azz_id)
    # id_of_who_referred = session.get("id_of_who_referred")

    # Add referee to the referees' list of the referral
    # if id_of_who_referred:
        # print("id of who referred found")
        # collection.update_one({"referral_code": id_of_who_referred}, {"$push":{"referees": unique_azz_id}})
    
    # insert_restaurant(collection, res_name, unique_azz_id, res_email, hashed_res_password, website_url, assistant_id, menu_file_id, menu_vector_id, currency, html_menu, qr_code=qr_code_id, wallet_public_key_address="None", wallet_private_key="None", location_coord=location_coord, location_name=location_name, id_of_who_referred=id_of_who_referred, logo_id=file_id)
    # send_confirmation_email_registered(mail, res_email, restaurant_name, FROM_EMAIL)
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
    if not session.get('access_granted_assistant_demo_chat'):
        abort(403)  # Forbidden
    user_message = 'Customer\'s message example'
    
    #ai_assist_response = get_assistants_response(user_message)

    messages = session.get('messages', [])
    messages = []

    # print(len(messages))

    #if len(messages) >= 4:
        #return redirect(url_for("setup_web_payments"))
    
    #response = get_assistants_response(user_message, CLIENT_OPENAI)

    restaurant_name = session.get('restaurant_name')
    
    if user_message:
        messages.append({'sender': 'assistant', 'content': f'Hello! I am your restaurant\'s AI-Assistant! Talk to me!'})
        messages.append({'sender': 'user', 'content': user_message})
        # Simulate the assistant's response
        messages.append({'sender': 'assistant', 'content': "I do not know what to say as I am not an AI yet. But in 7 seconds you will be redirected and magic will happen.", 'present':True})
    
    session['messages'] = messages
    print(messages)

    #send_waitlist_email(mail, verified_res_email, restaurant_name, FROM_EMAIL)

    # Clear the session variable after access
    session.pop('access_granted_assistant_demo_chat', None)
      
    session["access_granted_waitlist_page"] = True
    
    return render_template("start/demo.html", title="Demo Chat", messages=messages, restaurant_name=restaurant_name)

#################### Demo Chat Part End ####################





#################### Dashboard Part Main App ####################

@app.route('/ai-restaurants')
def market_dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 6
    search_query = request.args.get('location', '')
    radius = request.args.get('radius')
    user_lat = request.args.get('user_lat')
    user_lng = request.args.get('user_lng')

    restaurants, total = get_restaurants(page, per_page, search_query, user_lat, user_lng, radius)

    if not restaurants and radius:
        flash(f"No restaurants are found in {radius} km radius from you.", "warning")
        restaurants, total = get_restaurants(page, per_page, search_query)

    return render_template(
        'marketing_dashboard/market_dashboard.html', 
        restaurants=restaurants, 
        page=page, 
        per_page=per_page, 
        total=total, 
        title="Restaurants List with AI Sprinkle", 
        search_query=search_query, 
        GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY,
        current_radius = radius
    )



def get_restaurants(page, per_page, search_query='', user_lat=None, user_lng=None, radius=None):
    skip = (page - 1) * per_page
    cursor = collection.find()
    restaurants = list(cursor)

    if search_query:
        search_terms = [term.strip().lower() for term in search_query.split(',')]
        filtered_restaurants = [r for r in restaurants if any(term in r.get('location_name', '').lower() for term in search_terms) and r.get('profile_visible', False)]
    else:
        filtered_restaurants = [r for r in restaurants if r.get('profile_visible', True)]

    # If user location and radius are provided, filter by distance
    if user_lat and user_lng and radius:
        user_coords = (float(user_lat), float(user_lng))
        radius_km = float(radius)

        # print(user_coords)
        # print("Type of filtered restaurants: ", type(filtered_restaurants))
        # print(filtered_restaurants)
        
        filtered_restaurants = [
            r for r in filtered_restaurants 
            if geodesic(user_coords, (json.loads(r['location_coord'])['lat'], json.loads(r['location_coord'])['lng'])).km <= radius_km
        ]

        print()

        # Sort restaurants by distance
        filtered_restaurants.sort(
            key=lambda r: geodesic(user_coords, (json.loads(r['location_coord'])['lat'], json.loads(r['location_coord'])['lng'])).km
        )

    total = len(filtered_restaurants)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_restaurants = filtered_restaurants[start:end]

    return paginated_restaurants, total


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard_display(show_popup=False):
    if request.args.get("show_popup") == "True":
        show_popup = True
      
    PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID")

    print("Jumped on display dashboard link")
    res_email = session.get("res_email")
    res_password = session.get("password")

    

    # Find the instance in MongoDB
    restaurant_instance = collection.find_one({"email": res_email}) 

    # Check if the instance exists
    if restaurant_instance:
        # Retrieve the necessary values from the instance
        restaurant_name = restaurant_instance.get("name")
        restaurant_website_url = restaurant_instance.get("website_url")
        restaurant_email = restaurant_instance.get("email")
        
        res_acc_password = restaurant_instance.get("password")
        is_google_acc = res_acc_password == "google_acc"
        
        assistant_id = restaurant_instance.get("assistant_id")
        web3_wallet_address = restaurant_instance.get("web3_wallet_address")
        current_balance = restaurant_instance.get("balance")
        current_balanceHigherThanTwentyCents = round(current_balance, 2) >= 0.2
        print(f"Balance is higer than 20 cents: {current_balanceHigherThanTwentyCents}")
        res_unique_azz_id = restaurant_instance.get("unique_azz_id")
        awaiting_withdrawal = restaurant_instance.get("await_withdrawal")
        res_currency = restaurant_instance.get("res_currency")
        html_menu = restaurant_instance.get("html_menu_tuples")
        discovery_mode = restaurant_instance.get("discovery_mode")
        assistant_spent = restaurant_instance.get("assistant_fund")
        default_menu = False
        delivery_offered = restaurant_instance.get("delivery_offered")
        delivery_radius = restaurant_instance.get("radius_delivery_value")
        menu_vector_id = restaurant_instance.get("menu_vector_id")
        if menu_vector_id == MOM_AI_EXEMPLARY_MENU_VECTOR_ID:
            default_menu = True
        logo_id = restaurant_instance.get("res_logo", "666af654dee400a1d635eb08")
        qr_code_id = restaurant_instance.get("qr_code", "666af654dee400a1d635eb08")
        gateway_is_on = restaurant_instance.get("paymentGatewayTurnedOn")
        referral_id = restaurant_instance.get("referral_code")
        referees_list = restaurant_instance.get("referees", [])
        num_of_referees = len(referees_list) 
        ai_phone_number = restaurant_instance.get("ai_phone_number")
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
        session["html_menu_tuples"] = html_menu
        session["qr_code_id"] = qr_code_id
        session["default_menu"] = default_menu
        session["ai_phone_number"] = ai_phone_number

        print(f"Assistant ID added in session: {assistant_id}")
        print(f"Restaurant name added in session: {restaurant_name}")
        print(f"Unique azz id added in session: {res_unique_azz_id}")
        
        if logo_id == None:
            logo_id = "666af654dee400a1d635eb08"
        
        logo_url = url_for('serve_image', file_id=logo_id)

    else:
        # Handle the case when the instance is not found
        flash("Restaurant not found. Please, login with the right credentials.")
        return redirect(url_for("login"))
    return render_template("dashboard/dashboard.html", 
                           title=f"{restaurant_name}\'s Dashboard", 
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
                           res_currency="EUR",  # res_currency=res_currency,
                           assistant_turned_on=assistant_turned_on,
                           logo_url=logo_url,
                           restaurant=restaurant_instance,
                           exchange_api_key=EXCHANGE_API_KEY,
                           gateway_is_on=gateway_is_on,
                           show_popup=show_popup,
                           PAYPAL_CLIENT_ID=PAYPAL_CLIENT_ID,
                           default_menu=default_menu,
                           referral_id=referral_id,
                           num_of_referees=num_of_referees,
                           discovery_mode=discovery_mode,
                           delivery_offered=delivery_offered,
                           delivery_radius=delivery_radius,
                           current_balanceHigherThanTwentyCents=current_balanceHigherThanTwentyCents,
                           is_google_acc=is_google_acc)


@app.route('/splash-page/<unique_azz_id>', methods=['POST', 'GET'])
def splash_page_display(unique_azz_id):
    restaurant = collection.find_one({"unique_azz_id": unique_azz_id})
    return render_template("splash_page/splash_page.html", restaurant=restaurant, unique_azz_id=unique_azz_id)


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

    # print("Payments passed: ", payments)

    there_are_payments = True if len(payments)>=1 else False

    # print(f"\n\nPayments Retrieved\n\n")

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

@app.route('/delivery_offered_toggler', methods=['POST'])
def delivery_offered_gateway():
    data = request.get_json()
    print(data)
    deliveryOfferedTurnedOn = data.get('delivery_offered_turned_on', None)
    radiusDeliveryKm = data.get('radius', None)
    
    if deliveryOfferedTurnedOn is not None:
        print(f"Delivery offered toggled: {deliveryOfferedTurnedOn}")

        unique_azz_id = session.get("unique_azz_id")
        print(unique_azz_id)
        collection.update_one({"unique_azz_id":unique_azz_id}, {"$set":{"delivery_offered": deliveryOfferedTurnedOn}})
    
    if radiusDeliveryKm is not None:
        print(f"Radius delivery value: {radiusDeliveryKm}")

        unique_azz_id = session.get("unique_azz_id")
        print(unique_azz_id)
        collection.update_one({"unique_azz_id":unique_azz_id}, {"$set":{"radius_delivery_value": int(radiusDeliveryKm)}})
    
    # Respond with the new state
    return jsonify({'delivery_offered_turned_on': deliveryOfferedTurnedOn, 'ok':True})

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

@app.route('/discovery_mode_toggler', methods=['POST'])
def toggle_discovery_mode():
    data = request.get_json()
    discovery_mode = data.get('discovery_mode')
    print(f"discovery_mode: {discovery_mode}")

    unique_azz_id = session.get("unique_azz_id")
    print(unique_azz_id)
    collection.update_one({"unique_azz_id":unique_azz_id}, 
                          {"$set":{"discovery_mode": discovery_mode}})

    # Respond with the new state
    return jsonify({'discovery_mode': discovery_mode})

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
def update_profile(attribute, tg_setup=None):
    print("Tg setup on start: ", tg_setup )
    
    if attribute == "notif_destin":
        if tg_setup is None:
            print("Request args get tg setup: ", request.args.get("tg_setup"))
            tg_setup = request.args.get("tg_setup") == "True"
    if tg_setup:
        session["access_for_setup_public_profile_page"] = False
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
            # Step 1: Remove extra spaces and split by comma
            str_list = new_value.split(',')

            print("entered tg route")

            print("Tg setup is ", tg_setup)

            # Step 2: Convert each element to an integer, strip any leading/trailing whitespace
            id_list = [num.strip() for num in str_list]
            for id in id_list:
                if id not in restaurant.get("notif_destin", []):
                    collection.update_one({'unique_azz_id': current_uni_azz_id},{'$push': {'notif_destin': id}})
                    NEW_CHAT_MESSAGE = f"🔝You are the best\n\nYou have successfully setup notifications!\n\nMOM AI bot will notify you upon upcoming of new orders in this chat.\n\nNow you should go to the 'Assistant' tab and start using your MOM AI Restaurant Assistant!"
                    send_telegram_notification(id, message=NEW_CHAT_MESSAGE)
            if tg_setup:
                return redirect(url_for("update_menu_gui", initial_setup=True))
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
        if tg_setup:
            return redirect(url_for('dashboard_display', show_popup=True))
        else:
            # print("Chose not tg setup redirect")
            return redirect(url_for('dashboard_display'))
    else:
        print('Error in form submission!')
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in the {getattr(form, field).label.text} field - {error}", 'danger')
                print(f"Error in the {getattr(form, field).label.text} field - {error}")
    return render_template('settings/profile_update.html', 
                           form=form, 
                           attribute=attribute, 
                           restaurant=restaurant, 
                           title="Update Profile",
                           tg_setup=tg_setup)


@app.route('/setup_public_profile', methods=['GET', 'POST'])
def setup_public_profile():
    #if not session.get("access_for_setup_public_profile_page"):
        #abort(403)  # Forbidden
    
    form = ProfileForm()

    # unique_azz_id = session.get("unique_azz_id")

    # restaurant_name = collection.find_one({"unique_azz_id": unique_azz_id}).get("name")

    res_email = session.get("res_email")
    
    if form.validate_on_submit():
        website_url = form.website_url.data
        logo = form.logo.data
        description = form.description.data
        res_name = form.name.data
        print(res_name)
        locationName = form.locationName.data
        locationCoord = form.location.data
        print("location coord: ", locationCoord)
        id_of_who_referred = form.referral_id.data

        assistant, menu_vector_id, menu_file_id = create_assistant(res_name, "EUR", menu_path=None, client=CLIENT_OPENAI, menu_path_is_bool=False)
        unique_azz_id = res_name.lower().strip().replace(" ", "_").replace("'","")+"_"+assistant.id[-4:]

        qr_code_id = generate_qr_code_and_upload("https://mom-ai-restaurant.pro/splash-page/"+unique_azz_id, unique_azz_id) #assistant_code

        print(f"Type of qr code id: {type(qr_code_id)}")
        print("We are past qr code function")
        qr_code_id = str(qr_code_id)

        print(website_url, logo, description)
        
        res_password = session.get("password", "google_acc")
        if res_password != "google_acc":
            hashed_res_password = hash_password(res_password)
        else:
            hashed_res_password = res_password
        
        # Add referee to the referees' list of the referral
        if id_of_who_referred:
            print("id of who referred found")
            collection.update_one({"referral_code": id_of_who_referred}, {"$push":{"referees": unique_azz_id}})
        
        video_url = create_and_get_talk_video(f"Hi, welcome to {res_name}! How can I help you?")
        intro_file_name = f"intro_{unique_azz_id}.mp4"
        full_intro_in_momai_google(video_url, intro_file_name)
        print("Uploaded AI-Intro")

        session["unique_azz_id"] = unique_azz_id
        session["assistant_id"] = assistant.id
        
        insert_restaurant(
    collection=collection,
    name=res_name,
    unique_azz_id=unique_azz_id,
    email=res_email,
    password=hashed_res_password,
    website_url=website_url,
    assistant_id=assistant.id,
    menu_file_id=MOM_AI_EXEMPLARY_MENU_FILE_ID,
    menu_vector_id=MOM_AI_EXEMPLARY_MENU_VECTOR_ID,
    currency="EUR",
    html_menu=MOM_AI_EXEMPLARY_MENU_HTML,
    qr_code=qr_code_id,
    wallet_public_key_address=None,
    wallet_private_key=None,
    location_coord=locationCoord,
    location_name=locationName,
    id_of_who_referred=id_of_who_referred,
    logo_id="666af654dee400a1d635eb08",
)
        
        # Handle file upload and other logic here
        if logo:
            image = form.logo.data
            filename = secure_filename(image.filename)
            file_id = fs.put(image, filename=filename)
            print(f'Raw file id {file_id} and string file id {str(file_id)}')
            collection.update_one({'unique_azz_id': unique_azz_id}, {'$set': {'res_logo': file_id}}) 
        
        if website_url:
            collection.update_one({"unique_azz_id": unique_azz_id}, {"$set":{"website_url": website_url}})
        
        if description:
            collection.update_one({'unique_azz_id': unique_azz_id}, {'$set': {'description': description}}) 
        
        # flash('Public profile setup successfully!', 'success')
        return redirect(url_for('update_profile', attribute="notif_destin", tg_setup=True))

    
    
    return render_template('start/setup_public_profile.html', 
                           form=form,
                           title="Setup Public Profile",
                           GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY)







@app.route('/set-working-hours')
def set_working_hours(start_setup=False):
    start_setup = request.args.get("start_setup") == "True"
    print("Start setup on server: ", start_setup)
    current_uni_azz_id = session.get("unique_azz_id")
    restaurant = collection.find_one({'unique_azz_id': current_uni_azz_id})

    start_hours = [day["start"] for day in restaurant["working_schedule"]]
    end_hours = [day["end"] for day in restaurant["working_schedule"]]
    dayOffzz = [day["dayOff"] for day in restaurant["working_schedule"]]
    print(dayOffzz)

    current_rest_timezone = restaurant.get('timezone', None)
    print(f"Current restaurant timezone: ", current_rest_timezone)

    if start_setup:
        session["access_for_setup_public_profile_page"] = True

    return render_template('settings/set_working_hours.html', 
                           title="Set Working Hours", 
                           start_hours=start_hours, 
                           end_hours=end_hours, 
                           restaurant=restaurant, 
                           current_rest_timezone=current_rest_timezone,
                           start_setup=start_setup,
                           day_Offzz=dayOffzz)


@app.route('/submit_hours', methods=['POST'])
def submit_hours():
    working_hours = request.json['schedule']
    timezone = request.json['timezone']
    # Process the working hours as needed
    # For now, we'll just print them
    print(working_hours)
    current_uni_azz_id = session.get("unique_azz_id")
    restaurant = collection.find_one({'unique_azz_id': current_uni_azz_id})
    
    working_hours = list(working_hours.values())
    """
    for day, times, dayOff in working_hours.items():
        if not times['start'] is None and not times['end'] is None:
            start_values.append(times['start'])
            end_values.append(times['end'])
            day_off_bool.append(times['dayOff'])
        else: 
            start_values.append(777)
            end_values.append(777)
    print("Lists we passed: ", start_values, end_values)
    """
    
    result = collection.update_one({'unique_azz_id': current_uni_azz_id}, {'$set':{"working_schedule": working_hours, "timezone":timezone}})
    # print("\nUpdated successfully\n")
    flash("The working hours were updated successfully", "success")

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
        return jsonify({"message":f"<p style='color: green;'>The review has been successfully placed and {amount_to_send} MOM tokens added to your balance.\nTo check the transaction <a href='https://amoy.polygonscan.com/tx/{tx_hash}' target='_blank'>click here.</a></p>", "tx_hash":tx_hash, "success":True})
    else:
        return jsonify({"message":f"<p>The review has been successfully placed and {amount_to_send} MOM tokens added to your balance.</p>", "tx_hash":tx_hash, "success":True})

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
    unique_azz_id = session.get("unique_azz_id")
    restaurant = collection.find_one({"unique_azz_id": unique_azz_id})

    html_menu_tuples = restaurant.get("html_menu_tuples")
    default_menu = session.get("default_menu")
    
    res_currency = session.get("res_currency")
    # wrapped_html_table = wrap_images_in_html_table(html_menu)
    print("Default menu we pass: ", default_menu)

    # print("That's the menu we've got ", wrapped_html_table)
    return render_template("dashboard/menu_display.html", 
                           html_menu_tuples=html_menu_tuples, 
                           form=form,
                           default_menu=default_menu,
                           unique_azz_id=unique_azz_id,
                           res_currency=res_currency)

    
"""
@app.route('/update_menu', methods=['GET', 'POST'])
def update_menu():
    if request.method == 'POST':
        menu_format = request.form.get('menu_format')
        currency_ticker = request.form.get('currency')

        if menu_format == 'file':
            files = request.files.getlist('menu_files')
            file_paths = []
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    file_paths.append(file_path)
            # Handle the uploaded file paths here
            process_files(file_paths)

        elif menu_format == 'link':
            links = request.form.get('menu_links')
            link_list = links.split('\t')  # Assuming links are separated by tabs
            # Handle the links here
            process_links(link_list)

        elif menu_format == 'image':
            images = request.files.getlist('menu_images')
            image_paths = []
            for image in images:
                if image and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image.save(image_path)
                    image_paths.append(image_path)
            # Handle the uploaded image paths here
            process_images(image_paths)

        flash('Menu data processed successfully!')
        return redirect(url_for('update_menu'))

    return render_template('upload_menu.html')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'txt', 'docx', 'xlsx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename(filename):
    return filename.replace(' ', '_')
"""


@app.route('/set-currency', methods=['POST'])
def set_currency(initial_setup=False):
    initial_setup = request.args.get("initial_setup") == "True"

    print("\n\n\nInitial setup - ", initial_setup, "\n\n\n")

    unique_azz_id = session.get("unique_azz_id")
    new_currency = request.form.get("currency")

    result = collection.update_one({"unique_azz_id": unique_azz_id}, {"$set":{"res_currency":new_currency}})

    flash(f"Set the currency of your menu to {new_currency}", category="success")

    if initial_setup:
        return redirect(url_for("update_menu_gui", initial_setup=True))
    else:
        return redirect(url_for("update_menu_gui"))


@app.route('/update_menu', methods=['POST'])
def update_menu(initial_setup=False):

    initial_setup = request.args.get("initial_setup") == "True"

    print("\n\n\nInitial setup - ", initial_setup, "\n\n\n")

    try:
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
        restaurant = collection.find_one({"unique_azz_id": unique_azz_id})
        assistant_id = restaurant.get("assistant_id")

        upload_response = upload_new_menu(menu_xlsx_path, menu_save_txt_path, currency, restaurant_name, collection, unique_azz_id, assistant_id)
        print(upload_response)

        
        restaurant = collection.find_one({"unique_azz_id": unique_azz_id})    

        
        if upload_response["success"]:
            voice_pathway_id = restaurant.get("voice_pathway_id", None)

            if voice_pathway_id:
                unique_azz_id = session.get("unique_azz_id")
                restaurant = collection.find_one({"unique_azz_id": unique_azz_id})
                
                restaurant_menu_tuples = restaurant.get("html_menu_tuples")

                menu_string = ""

                for item in restaurant_menu_tuples:
                    item_text = f"Name: {item['Item Name']}\nIngredients: {item['Item Description']}\nPrice: {item['Item Price (EUR)']} EUR\n\n\n"
                    menu_string += item_text
                
                restaurant_name = restaurant.get("name")
                store_location = restaurant.get("location_name")
                timezone = restaurant.get("timezone")
                restaurant_menu = menu_string
                
                opening_hours_string = ""

                opening_closing_hours_tuple = zip(restaurant.get("start_work"), restaurant.get("end_work"))

                day_of_weeks = {
                    0: 'Monday',
                    1: 'Tuesday',
                    2: 'Wednesday',
                    3: 'Thursday',
                    4: 'Friday',
                    5: 'Saturday',
                    6: 'Sunday'
                }

                for index, (start_time, end_time) in enumerate(opening_closing_hours_tuple):
                    day_of_week = day_of_weeks[index]
                    opening_hours_line = f"{day_of_week}: from {start_time} until {end_time}" if end_time <= 24 else f"{day_of_week}: from {start_time} until {end_time-24} of the next day"
                    opening_hours_string += opening_hours_line + "\n"
                
                create_the_suitable_pathway_script(restaurant_name, store_location, opening_hours_string, timezone, restaurant_menu, unique_azz_id)

                success = insert_the_nodes_and_edges_in_new_pathway(voice_pathway_id, unique_azz_id)
            flash("Menu updated successfully!", category="success")
            session["default_menu"] = False
        else:
            flash("Error updating menu. Please check the file for validity.", category="danger")
    except Exception as e:
            flash(f"Error updating menu. Please check the file for validity. Error message: {e}", category="danger")
            return redirect(url_for("update_menu_gui"))

    if initial_setup:
        return redirect(url_for("set_working_hours", start_setup=True))
    else:
        return redirect(url_for("update_menu_gui"))
    

@app.route('/trigger_generate_menu_item_image', methods=['POST'])
def trigger_generate_menu_item_image():
    data = request.get_json()
    item_name = data.get('item_name')
    item_description = data.get('item_description')
    unique_azz_id = session.get('unique_azz_id')

    # Here, call your AI-image generation logic based on item_name and item_description
    # Assume we have a function that returns a link to the generated image
    start_time = time.time()

    generated_link_task = generate_ai_menu_item_image_celery.apply_async(
        args=[
            item_name, item_description, unique_azz_id
            ])

    # print(f"It took {time.time()-start_time} seconds to generate the image")

    if generated_link_task:
        return jsonify({"task_id": generated_link_task.id}), 202
    else:
        return jsonify({'error': 'Image generation failed'}), 500
    
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 16MB max upload size

# The endpoint to handle the form submission and file uploads
@app.route('/upload_full_menu_picture', methods=['POST', 'GET'])
def upload_full_menu_picture():
    last_part = "/update_menu_gui"

    print(f"Redirect URL: {last_part}")
    print(f"Request Files: {request.files}")

    if 'menu_images' not in request.files:
        flash('No files part')
        return redirect(last_part)
    
    files = request.files.getlist('menu_images')

    print("Files: ", files)

    # Limit the number of files to 4
    if len(files) > 4:
        flash('You can upload a maximum of 4 files.')
        return redirect(last_part)
    
    bucket_name = "mom-ai-restaurant-pictures"
    unique_azz_id = session.get("unique_azz_id")

    for index, file in enumerate(files):
        if file and allowed_file(file.filename):
            file_name = secure_filename(file.filename)
            file.save(file_name)
            
            unique_azz_id = session.get("unique_azz_id")
            
            # Upload the file to S3
            folder_name = unique_azz_id+"_menu_picture"
            object_name = unique_azz_id+"_menu_picture_"+str(index)+"_"+file_name
            
            try:
                google_menu_image_link = upload_file_google(file_name, folder_name=folder_name)

                os.remove(file_name)
                
                # flash(f'File {file_name} successfully uploaded to S3!')
                # google_menu_image_link = f"https://{bucket_name}.s3.eu-north-1.amazonaws.com/{folder_name}/{object_name}"
                
                
                collection.update_one({"unique_azz_id": unique_azz_id}, {"$push": {"menu_images": google_menu_image_link}})
            except Exception as e:
                print(f'Error uploading {file_name} to S3: {str(e)}')
                flash(f'Error uploading {file_name} to S3: {str(e)}')
                return redirect(last_part)
        else:
            flash(f'File {file.filename} is not allowed.')
            return redirect(last_part)
    flash('All files successfully uploaded!')
    return redirect(last_part)



@app.route('/generate_menu_item_image_status/<task_id>', methods=['GET'])
def generate_menu_image_task_status(task_id):
    task = celery.AsyncResult(task_id)

    print("Task state: ", task.state)

    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state == 'SUCCESS':
        aws_image_link = task.result
        
        response = {
            'state': task.state,
            'image_link': aws_image_link,  # Task result when completed
            'status': 'Task completed!'
        }
    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'status': str(task.info)  # Exception message if failed
        }
    else:
        response = {
            'state': task.state,
            'status': task.state  # Other states like 'RETRY'
        }

    return jsonify(response)



# Flask route to handle the description generation
@app.route('/generate_item_description', methods=['POST'])
def generate_description():
    data = request.get_json()

    # Check if 'item_name' is provided in the request
    if not data or 'item_name' not in data:
        return jsonify({'error': 'Missing item name'}), 400

    item_name = data['item_name']
    unique_azz_id = session.get("unique_azz_id")

    # Generate the description using your logic
    item_description, tokens_used = generate_ai_item_description(item_name)

    charge_for_generation = PRICE_PER_1_TOKEN*tokens_used

    print(f"Charge calculated: {charge_for_generation} EUR")
    
    collection.update_one({"unique_azz_id": unique_azz_id}, {"$inc": {"balance": -charge_for_generation, "assistant_fund": charge_for_generation}})

    # Return the description as JSON
    return jsonify({'item_description': item_description}), 200




@app.route('/update_menu_manual', methods=['POST'])
def update_menu_manual():
    data = request.json  # Get the JSON data from the request

    print(data)

    unique_azz_id = data.get("unique_azz_id")
    updated_items = data.get("updatedItems")

    restaurant = collection.find_one({"unique_azz_id": unique_azz_id})

    # Convert the list of dictionaries to a text format
    menu_text = ""
    for item in updated_items:
        menu_text += f"Item Name: {item.get('Item Name')}, "
        menu_text += f"Item Description: {item.get('Item Description')}, "
        menu_text += f"Item Price (EUR): {item.get('Item Price (EUR)')}, "
        if item.get("Link to Image"):    
            menu_text += f'Item\'s Image: <img src="{item.get("Link to Image")}" alt="Image of {item.get("Item Name")}" width="170" height="auto">'
        if item.get("ai_image_url"):
            menu_text += f'AI-generated Item Image: <img src="{item.get("ai_image_url")}" alt="AI-generated image of {item.get("Item Name")}" width="170" height="auto">'
        menu_text += "\n"  # Add a newline for better readability

    # Save the text to a .txt file
    file_name = 'uploads/new_menu.txt'
    with open(file_name, 'w') as file:
        file.write(menu_text)

    with open(str(file_name), "rb") as menu:    
        client = CLIENT_OPENAI

        menu_file = client.files.create(file=menu, purpose='assistants')
        menu_file_id = menu_file.id  

        restaurant_name = restaurant.get("name") 
        assistant_id = restaurant.get("assistant_id") 
        
        # Create a vector store called "Financial Statements"
        vector_store = client.beta.vector_stores.create(name=f"{restaurant_name} Menu")
        
        # Ready the files for upload to OpenAI
        file_paths = [file_name]
        file_streams = [open(path, "rb") for path in file_paths]
        
        # Use the upload and poll SDK helper to upload the files, add them to the vector store,
        # and poll the status of the file batch for completion.
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=file_streams
        )

        assistant = client.beta.assistants.update(
            assistant_id=assistant_id,
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )

        average_menu_price = statistics.mean([float(item["Item Price (EUR)"]) for item in updated_items])

        collection.update_one({"unique_azz_id": unique_azz_id}, 
                              {"$set": {"menu_file_id": menu_file_id, 
                                "menu_vector_id": vector_store.id, 
                                "html_menu_tuples": updated_items, 
                                "average_menu_price": average_menu_price}})
    
    voice_pathway_id = restaurant.get("voice_pathway_id")

    if voice_pathway_id:
        unique_azz_id = session.get("unique_azz_id")
        restaurant = collection.find_one({"unique_azz_id": unique_azz_id})
        
        restaurant_menu_tuples = restaurant.get("html_menu_tuples")

        menu_string = ""

        for item in restaurant_menu_tuples:
            item_text = f"Name: {item['Item Name']}\nIngredients: {item['Item Description']}\nPrice: {item['Item Price (EUR)']} EUR\n\n\n"
            menu_string += item_text
        
        restaurant_name = restaurant.get("name")
        store_location = restaurant.get("location_name")
        timezone = restaurant.get("timezone")
        restaurant_menu = menu_string
        
        opening_hours_string = ""

        opening_closing_hours_tuple = zip(restaurant.get("start_work"), restaurant.get("end_work"))

        day_of_weeks = {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thursday',
            4: 'Friday',
            5: 'Saturday',
            6: 'Sunday'
        }

        for index, (start_time, end_time) in enumerate(opening_closing_hours_tuple):
            day_of_week = day_of_weeks[index]
            opening_hours_line = f"{day_of_week}: from {start_time} until {end_time}" if end_time <= 24 else f"{day_of_week}: from {start_time} until {end_time-24} of the next day"
            opening_hours_string += opening_hours_line + "\n"
        
        create_the_suitable_pathway_script(restaurant_name, store_location, opening_hours_string, timezone, restaurant_menu, unique_azz_id)

        success = insert_the_nodes_and_edges_in_new_pathway(voice_pathway_id, unique_azz_id)
    # Return a success response
    session["default_menu"] = False

    flash("Menu updated successfully!", category="success")
    

    return jsonify({"success":True})

@app.route('/update_menu_gui')
def update_menu_gui(initial_setup=None):
    initial_setup = request.args.get("initial_setup") == "True"
    form = UpdateMenuForm()
    default_menu = session.get("default_menu")
    unique_azz_id = session.get("unique_azz_id")

    session["initial_setup"] = True

    restaurant = collection.find_one({"unique_azz_id":unique_azz_id})

    html_menu_tuples = restaurant.get("html_menu_tuples")

    if not html_menu_tuples:
        html_menu_tuples = [{"Item Name": "Test Name", "Item Description": "Test Description", "Item Price (EUR)": 300}]

    print(html_menu_tuples)

    # wrapped_html_table = wrap_images_in_html_table(html_menu)

    currency = restaurant.get("res_currency")

    menu_vector_id = restaurant.get("menu_vector_id")

    menu_images = restaurant.get("menu_images", [])
    print("Menu image we pass: ", menu_images)
    
    if menu_vector_id == MOM_AI_EXEMPLARY_MENU_VECTOR_ID:
        default_menu = True
    else:
        default_menu = False

    # print("That's the menu we've got ", wrapped_html_table)
    return render_template("settings/menu_edit.html", 
                           html_menu_tuples=html_menu_tuples, 
                           form=form,
                           default_menu=default_menu,
                           unique_azz_id=unique_azz_id,
                           title="Edit Menu",
                           initial_setup=initial_setup,
                           currency=currency,
                           menu_images=menu_images)


@app.route('/delete_menu_image', methods=['POST'])
def delete_menu_image():
    data = request.get_json()
    image_url = data.get('image_url')
    
    unique_azz_id = session.get("unique_azz_id")

    object_key = '/'.join(image_url.split('/')[-2:])

    try:
        delete_file_by_url_google(image_url)
        # Remove the image from the database (assuming S3 image URLs are stored in the "menu_images" field)
        collection.update_one(
            {"unique_azz_id": unique_azz_id},
            {"$pull": {"menu_images": image_url}}
        )

        # Optionally, delete the image from S3 (if stored on S3)
        # s3.delete_object(Bucket=bucket_name, Key=image_url.split('/')[-1])  # Example of deleting from S3

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Mint MOM token
@app.route('/mint-send-tokens', methods=['POST'])
def mint_tokens():
    data = request.json
    wallet_address = data['wallet_address']
    amount = data['amount']

    sending = mint_and_send_tokens(wallet_address, amount)

    tx_hash = sending["tx_hash"]

    hide_wallet_button = True

    flash(f"Congratulations! You have successfully received 50 MOM tokens!\nTransaction hash: {tx_hash}", "success")

    return jsonify({
        'ok': True,
        'transaction_hash': tx_hash,
        "hide_wallet_button": hide_wallet_button
    })


########## Menu Extraction from the Menu ##############

@app.route('/trigger_extract_menu_from_image', methods=['POST'])
def trigger_extract_menu_from_image():
    request_url = "/update_menu_gui"
    
    if 'menu_images_extract_menu' not in request.files:
        flash('No files part')
        return redirect("")
    
    files = request.files.getlist('menu_images_extract_menu')

    print("Files: ", files)
    
    image_paths = []
    for index, file in enumerate(files):
        file.save(file.filename)
        if file and allowed_file(file.filename):
            url = upload_file_google(file.filename, folder_name="temp_files")
            if url:
                image_paths.append(url)  # Append the URL to the list
            else:
                print(f"Failed to upload {file.filename}")
    print("Image Paths we pass: ", image_paths)

    cache.set("image_url_links", image_paths)

    generated_link_task = fully_extract_menu_from_image_celery.apply_async(
        args=[
            image_paths
            ])

    # print(f"It took {time.time()-start_time} seconds to generate the image")

    if generated_link_task:
        return jsonify({"task_id": generated_link_task.id}), 202
    else:
        return jsonify({'error': 'Image generation failed'}), 500
    

@app.route('/extract_menu_from_image_status/<task_id>', methods=['GET'])
def generate_extract_menu_from_image_status(task_id):
    
    task = celery.AsyncResult(task_id)

    unique_azz_id = session.get("unique_azz_id")
    image_paths = cache.get("image_url_links")

    print("Task state: ", task.state)

    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state == 'SUCCESS':
        menu_list = task.result[0]
        amount_to_charge = task.result[1]

        collection.update_one(
            {"unique_azz_id": unique_azz_id}, 
            {"$inc": {"balance": -amount_to_charge, "assistant_fund": amount_to_charge}}
        )
        
        # clean_the_temp_folder()
        
        response = {
            'state': task.state,
            'menu_list': menu_list,  # Task result when completed
            'status': 'Task completed!'
        }
        for url in image_paths:
            delete_file_by_url_google(url)
    elif task.state == 'FAILURE':
        # clean_the_temp_folder()
        response = {
            'state': task.state,
            'status': str(task.info)  # Exception message if failed
        }
        for url in image_paths:
            delete_file_by_url_google(url)
    else:
        # clean_the_temp_folder()
        response = {
            'state': task.state,
            'status': task.state  # Other states like 'RETRY'
        }

    return jsonify(response)


def clean_the_temp_folder():
    # Define the folder path
    folder_path = '/tmp'

    # Use glob to get all files in the folder (with pattern '*')
    files = [file.replace("\\", "/") for file in glob.glob(os.path.join(folder_path, '*'))]

    # Iterate over the files and remove them
    for file in files:
        try:
            os.remove(file)  # Remove the file
            print(f'Removed: {file}')
        except Exception as e:
            print(f'Error deleting {file}: {e}')


@app.route('/handle_ai_generated_menu', methods=['POST'])
def handle_ai_generated_menu():
    print("Entered handle_ai_generated_menu route")

    # Get the menu items from the request body
    data = request.get_json()
    print(f"Received request data: {data}")

    new_menu_items = data.get('menu_items', [])
    print(f"Extracted new menu items: {new_menu_items}")

    # Check if we are appending or replacing
    append = request.args.get('append', 'False').lower() == 'true'
    replace = request.args.get('replace', 'False').lower() == 'true'
    print(f"Append mode: {append}, Replace mode: {replace}")

    # Get the unique_azz_id from session
    unique_azz_id = session.get("unique_azz_id")
    print(f"Unique Azz ID: {unique_azz_id}")

    # Initial check for operation type
    if append:
        # Fetch the current menu
        current_menu = collection.find_one({"unique_azz_id": unique_azz_id})["html_menu_tuples"]
        if current_menu:
            print(f"Found current menu for unique_azz_id {unique_azz_id}: {current_menu}")
        else:
            print(f"No current menu found for unique_azz_id {unique_azz_id}")
            current_menu = []

        # Append new items to the existing menu
        current_menu.extend(new_menu_items)
        new_menu = current_menu
        print(f"New appended menu: {new_menu}")

    elif replace:
        # Replace the entire menu with new items
        new_menu = new_menu_items
        print(f"New menu replacing the existing menu: {new_menu}")
    else:
        print(f"Invalid operation. Neither append nor replace selected.")
        return jsonify({'success': False, 'message': 'Invalid operation'}), 400

    # Attempt to update the menu in the database
    print(f"Updating the menu for unique_azz_id {unique_azz_id} with new menu: {new_menu}")
    result = collection.update_one({"unique_azz_id": unique_azz_id}, {"$set": {"html_menu_tuples": new_menu}})
    print(f"Update result: {result.raw_result}")  # Print raw MongoDB result for detailed debug

    restaurant = collection.find_one({"unique_azz_id": unique_azz_id})
    currency = restaurant['res_currency']

    with open("temporary_text.txt", 'w', encoding='utf-8') as file:
        # Iterate through each row in the DataFrame
        for item in new_menu:
            file.write(f'Item Name: {item["Item Name"]} - Item Ingredients/Description: {item["Item Description"]} - Item Price in currency {currency}: {item["Item Price (EUR)"]}\n')

    update_menu_on_openai("temporary_text.txt", restaurant['assistant_id'], restaurant['name'])        

    os.remove("temporary_text.txt")

    if session.get("initial_setup"):
        return redirect(url_for("set_working_hours", start_setup=True))
    
    # Check if the update was successful
    if result.matched_count > 0:
        print(f"Menu updated successfully for unique_azz_id {unique_azz_id}")
        return jsonify({'success': True, 'message': 'Menu updated successfully!'})
    else:
        print(f"Failed to update menu for unique_azz_id {unique_azz_id}")
        return jsonify({'success': False, 'message': 'Failed to update menu'}), 500



#######################################################


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

@app.route('/payment_buffer/<unique_azz_id>/', methods=["POST", "GET"], defaults={'id': None})
@app.route('/payment_buffer/<unique_azz_id>/<id>', methods=['POST', 'GET'])
def payment_buffer(unique_azz_id, id):
    #if not id:
        #abort(403)  # Forbidden
    
    cache.set("access_granted_payment_result", True)

    restaurant = collection.find_one({"unique_azz_id":unique_azz_id})

    item_db = db_items_cache[unique_azz_id].find_one({"id":id})

    if item_db == None:
        items = cache.get("items_ordered")
    else:
        items = item_db.get("data")

    cache.set("items_ordered", items)
    print(f"Items on payment buffer: {items}")
    CURRENCY = restaurant.get("res_currency", "EUR")

    restaurant_menu = restaurant.get("html_menu_tuples")
    current_thread_id = session.get("current_thread_id")

    # print("Restaurant html menu tuples: \n\n\n", restaurant.get("html_menu_tuples"), "\n\n\n")

    res_currency = restaurant.get("res_currency")

    conversion_rate = cache.get("currency_rate")

    if res_currency != 'EUR':
        rate = c.convert(1, res_currency, 'EUR')
    else:
        rate = 1
        
    conversion_rate = rate

    #checkout_link = session.get("paypal_link")
    if restaurant['addFees']:
        addFees = True

        sum_of_order = sum(float(float(item['price'])*item['quantity']) for item in items)
        sum_of_order_euro = sum_of_order*conversion_rate

        fees_amount_EUR = 0.45+0.049*sum_of_order_euro
        fees_amount_native = round((0.45+0.049*sum_of_order_euro)/conversion_rate, 2)
        
        total_to_pay_str = str(sum_of_order_euro+fees_amount_EUR)
        total_to_pay_EUR = str(round(float(total_to_pay_str), 2))

        cache.set("sum_of_order", sum_of_order_euro)

        total_to_pay_native = str(round(float(total_to_pay_EUR)/conversion_rate, 2))

        
        print("Add fees on payment buffer")
    else:    
        addFees = False
        total_to_pay = sum(float(float(item['price'])*item['quantity']) for item in items)
        sum_of_order = total_to_pay
        
        total_to_pay_EUR = total_to_pay*conversion_rate
        total_to_pay_EUR = str(round(float(total_to_pay_EUR), 2))

        cache.set("sum_of_order", total_to_pay_EUR)

        total_to_pay_native = str(round(float(total_to_pay_EUR)/conversion_rate, 2))

        fees_amount_EUR = 0
        fees_amount_native = 0

    fees_amount = fees_amount_EUR

    cache.set("total_to_pay_EUR", total_to_pay_EUR)

    cache.set("total_to_pay_native", total_to_pay_native)
    
    total_to_pay_display = f"{float(total_to_pay_EUR):.2f}"

    cache.set("unique_azz_id", unique_azz_id)

    cache.set("items_ordered", items)
    cache.set("order_id", id)

    ordered_items_names = [item["name"] for item in items]

    image_urls = []

    for item_ordered_name in ordered_items_names:
        for item_menu in restaurant_menu:
            if sorted(item_menu["Item Name"].lower().split()) == sorted(item_ordered_name.lower().split()):
                print(sorted(item_menu["Item Name"].lower().split()))
                print(sorted(item_ordered_name.lower().split()))
                image_urls.append(item_menu.get("Link to Image"))
                found_match = True
                break
        if not found_match:
            image_urls.append(None)


    for index, image_url in enumerate(image_urls):
        items[index]['image_url'] = image_url

    print("Modified Items: ", items)
        

    
    return render_template("payment_routes/payment_buffer.html", total_to_pay_display=total_to_pay_display, 
                           items=items, 
                           total_to_pay_native=total_to_pay_native,
                           total_to_pay_EUR=total_to_pay_EUR, 
                           CLIENT_ID=CLIENT_ID, 
                           CURRENCY=CURRENCY, 
                           restaurant=restaurant, 
                           unique_azz_id=unique_azz_id, 
                           addFees=addFees, 
                           fees_amount=fees_amount, 
                           title="Payment Buffer",
                           sum_of_order=sum_of_order,
                           fees_amount_native=fees_amount_native,
                           fees_amount_EUR=fees_amount_EUR,
                           res_currency=res_currency,
                           current_thread_id=current_thread_id)


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
    print(top_up_balance, unique_azz_id, amount)
    if top_up_balance:
        id_of_who_referred_ = collection.find_one({'unique_azz_id': unique_azz_id})
        
        result_main = collection.update_one({'unique_azz_id': unique_azz_id}, {"$inc": {"balance": amount}})
        print("Updated the balance of the restaurant with ", unique_azz_id, " id")

        if id_of_who_referred_:
            id_of_who_referred = id_of_who_referred_.get("id_of_who_referred")
            if id_of_who_referred:
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
    # print(f"Received orderID: {orderID}")
    captured_order = captureOrder(orderID).json()
    # print("Captured Order: ", captured_order)

    if captured_order["status"] == "COMPLETED":
        return jsonify({"captured_order":captured_order, "topped_up_balance_manual":topped_up_balance})
    else:
        return jsonify({"error":True})


@app.route('/assistant_dash', methods=['POST', 'GET'])
def assistant_dashboard_route():
    
    sub_activated = session.get("subscription_activated")
    unique_azz_id = session.get("unique_azz_id")
    restaurant = collection.find_one({"unique_azz_id":unique_azz_id})
    restaurant_name = restaurant.get("name")
    qr_code_id = restaurant.get("qr_code")
    ai_phone_number = restaurant.get("ai_phone_number")
    default_menu = session.get("default_menu")

    return render_template("dashboard/assistant_reroute.html", unique_azz_id=unique_azz_id, restaurant_name=restaurant_name, 
                           sub_activated=sub_activated, 
                           qr_code_id=qr_code_id,
                           ai_phone_number=ai_phone_number,
                           default_menu=default_menu) 

#######################################################################################################


################### Voice Assistant Setup Start #########################


@app.route('/charge-for-call', methods=['POST'])
def charge_for_call():
    data = request.json
 
    print("Data we received: ", data)

    call_id = data.get("call_id")

    call_length, ai_phone_number = get_call_length_and_phone_number(call_id)

    price_of_call = call_length * PRICE_OF_MINUTE_PHONE_CALL

    print("Price of call and ai phone number: ", price_of_call, " Euros, ", ai_phone_number)

    result = collection.update_one({"ai_phone_number": ai_phone_number}, {"$inc":{"balance": -price_of_call}})

    if result.matched_count > 0:
        print("Successfully charged for the call.")
    
    return jsonify({"success": True})


@app.route('/purchase-phone-number', methods=['POST'])
def purchase_phone_number():
    data = request.form

    language = data.get("language")
    
    unique_azz_id = session.get("unique_azz_id")
    
    restaurant = collection.find_one({"unique_azz_id":unique_azz_id})

    restaurant_name = restaurant.get("name")

    pathway_id = restaurant.get("voice_pathway_id")

    timezone = restaurant.get("timezone")

    if restaurant.get("balance") <= 22.95:
        flash("Please top up your balance. You need at least 23 Euros on your account.", "danger")
        return redirect("/voice-setup")
    
    try:
        dict_response = buy_and_update_phone(pathway_id, language, timezone)
    except Exception as e:
        flash("There is an error on our side. Try again later!", "danger")
        return redirect("/voice-setup")
    
    phone_number = dict_response["phone_number"]

    # Get today's date
    today = datetime.today()

    # Extract the day number
    day_number = today.day

    # Modify the day if it exceeds 28
    if day_number > 28:
        today = today.replace(day=28)

    # Format the date as 'YYYY-MM-DD'
    formatted_date = today.strftime('%Y-%m-%d')

    result = collection.update_one({"unique_azz_id": unique_azz_id}, {"$set":{"ai_phone_number": phone_number, "ai_phone_subscription_date": formatted_date, "voice_pathway_lang":"en"} ,"$inc":{"balance": -20}})

    
    
    if result.matched_count > 0:
        flash(f"Congratulations! You have successfully setup {restaurant_name}'s Voice Assistant", "success")
        return redirect("/voice-setup")
    else:
        flash("We have got the phone number for you! It will arrive soon", "success")
        return redirect("/voice-setup")



@app.route('/update-ai-phone', methods=["POST"])
def update_phone_number_endpoint():
    language = request.form.get("language")
    unique_azz_id = session.get("unique_azz_id")

    restaurant = collection.find_one({"unique_azz_id": unique_azz_id})

    phone_number = restaurant.get("ai_phone_number")
    pathway_id = restaurant.get("voice_pathway_id")
    timezone = restaurant.get("timezone")

    print("Language we passed: ", language)
    
    restaurant_name = restaurant.get("restaurant_name")

    restaurant_name, store_location, opening_hours_string, timezone, restaurant_menu = get_data_for_pathway_change(restaurant)
    
    success_update = pathway_proper_update(restaurant_name, store_location, opening_hours_string, timezone, restaurant_menu, unique_azz_id, pathway_id, language)

    assert success_update
    
    success = update_phone_number(phone_number, language, timezone, pathway_id)

    collection.update_one({"unique_azz_id": unique_azz_id}, {"$set":{"voice_pathway_lang":language}})
    
    """
    if "en" in language:
        success = update_phone_number(phone_number, language, timezone, pathway_id)
    else:
        restaurant_menu_tuples = restaurant.get("html_menu_tuples")

        menu_string = ""

        for item in restaurant_menu_tuples:
            item_text = f"Name: {item['Item Name']}\nIngredients: {item['Item Description']}\nPrice: {item['Item Price (EUR)']} EUR\n\n\n"
            menu_string += item_text
        
        restaurant_name = restaurant.get("name")
        store_location = restaurant.get("location_name")
        timezone = restaurant.get("timezone")
        restaurant_menu = menu_string
        
        opening_hours_string = ""

        opening_closing_hours_tuple = zip(restaurant.get("start_work"), restaurant.get("end_work"))

        day_of_weeks = {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thursday',
            4: 'Friday',
            5: 'Saturday',
            6: 'Sunday'
        }

        for index, (start_time, end_time) in enumerate(opening_closing_hours_tuple):
            day_of_week = day_of_weeks[index]
            opening_hours_line = f"{day_of_week}: from {start_time} until {end_time}" if end_time <= 24 else f"{day_of_week}: from {start_time} until {end_time-24} of the next day"
            opening_hours_string += opening_hours_line + "\n"
        success = update_phone_number_non_english(phone_number, restaurant_name, restaurant_menu, opening_hours_string, store_location, language, timezone)
        print("Went through non-english path")
    """
    
    # print("Success: ", success, "New language: ", language)

    # success = False

    if success:
        flash("You have successfully updated the language of AI Phone Agent", "success")
        return redirect("/voice-setup")
    else:
        flash("Something went wrong. Try again!", "danger")
        return redirect("/voice-setup")
    


@app.route('/create-the-pathway', methods=['POST'])
def post_create_pathway():
    unique_azz_id = session.get("unique_azz_id")
    restaurant = collection.find_one({"unique_azz_id": unique_azz_id})

    restaurant_name, store_location, timezone, restaurant_menu, opening_hours_string = get_data_for_pathway_change(restaurant)
    
    result = pathway_serving_a_to_z_initial(restaurant_name, store_location, opening_hours_string, timezone, restaurant_menu, unique_azz_id)

    print("Success Creating Pathway??? ", result["success"])

    if not result["success"]:
        flash("Oops, something wrong on our side - try again!")
        return redirect('/voice-setup')

    pathway_id = result["pathway_id"]

    collection.update_one({"unique_azz_id": unique_azz_id}, {"$set":{"voice_pathway_id":pathway_id}})

    flash("Congratulations! Your voice agent has been successfully created!", "success")
    return redirect('/voice-setup')
    

@app.route('/post-phone-order', methods=['POST'])
def post_voice_order():
    raw_data = request.data
    print("Raw Data: ", raw_data)
    
    #data = request.json
    
    
    #print("JSON Data:", data)

    data = json.loads(raw_data.decode('utf-8'))

    unique_azz_id = data.get("unique_azz_id")
    from_number = data.get("from_number")

    restaurant = collection.find_one({"ai_phone_number": unique_azz_id})
    timezone = restaurant.get("timezone")
    if "+" in timezone:
        timezone = timezone.replace("+","-")
    elif "-" in timezone:
        timezone = timezone.replace("-","+")

    # Specify the desired time zone
    time_zone = pytz.timezone(timezone)  # Example: New York time zone

    # Get the current date and time in the specified time zone
    current_time = datetime.now(time_zone)

    # Format the date and time
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M')

    array_of_ordered_items = data.get("array_of_ordered_items")
    name_of_customer = data.get("name")

    total_paid = sum(item["price"] for item in array_of_ordered_items)

    orderID = generate_code()

    order_to_insert = {"items":array_of_ordered_items,
                       "orderID":orderID,
                       "timestamp": formatted_time,
                       "total_paid": total_paid,
                       "name_of_customer": name_of_customer,
                       "from_number": from_number,
                       "mom_ai_restaurant_fee": 0,
                       "paypal_fee": 0,
                       "paid": "NOT PAID",
                       "published": True
                       }
    
    db_order_dashboard[unique_azz_id].insert_one(order_to_insert)
 
    chat_ids = restaurant.get("notif_destin")

    if chat_ids:
        for chat_id in chat_ids:
            send_telegram_notification(chat_id)

    return jsonify({"success":True, "message":"Successful Posting of Voice Order!"})

@app.route('/voice-setup', methods=['GET', 'POST'])
def voice_setup_page():
    restaurant_name = session.get("restaurant_name")
    unique_azz_id = session.get("unique_azz_id")
    restaurant = collection.find_one({"unique_azz_id": unique_azz_id})


    voice_pathway_lang = restaurant.get("voice_pathway_lang")
    voice_pathway_id = restaurant.get("voice_pathway_id")
    ai_phone_number = restaurant.get("ai_phone_number")

    print(voice_pathway_lang)

    PAYPAL_CLIENT_ID = CLIENT_ID

    return render_template('voice-setup/voice_setup.html', 
                           title="Setup Phone Assistant",
                           restaurant_name=restaurant_name,
                           voice_pathway_id=voice_pathway_id,
                           restaurant=restaurant,
                           ai_phone_number=ai_phone_number,
                           unique_azz_id=unique_azz_id,
                           voice_pathway_lang=voice_pathway_lang,
                           PAYPAL_CLIENT_ID = PAYPAL_CLIENT_ID)

@app.route('/trigger_demo_call', methods=['POST'])
def trigger_demo_call():
    phone_number = request.form.get('phone_number')
    language = request.form.get('language')
    restaurant_name = session.get("restaurant_name")
    #restaurant_name = request.form.get('restaurant_name')

    unique_azz_id = session.get("unique_azz_id")
    restaurant = collection.find_one({"unique_azz_id": unique_azz_id})

    opening_hours_string = ""

    working_schedule = restaurant.get("working_schedule")

    start_work_list = []
    end_work_list = []
    day_off_list = []
    
    for day in working_schedule:
        start_work_list.append(day["start"])
        end_work_list.append(day["end"])
        day_off_list.append(day["dayOff"])

    opening_closing_hours_tuple = zip(start_work_list, end_work_list, day_off_list)

    day_of_weeks = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
    }

    
    for index, (start_time, end_time, dayOff) in enumerate(opening_closing_hours_tuple):
        day_of_week = day_of_weeks[index]
        if dayOff:
            opening_hours_line = f"{day_of_week}: day off"
        else:
            opening_hours_line = f"{day_of_week}: from {start_time} until {end_time}" if end_time <= 24 else f"{day_of_week}: from {start_time} until {end_time-24} of the next day"
        opening_hours_string += opening_hours_line

    store_location = restaurant.get("location_name")
    timezone = restaurant.get("timezone")

    print("The parameters we passed on send voice call endpoint: ", phone_number, language, restaurant_name)

    if phone_number and language:
        success = send_the_call_on_number_demo(phone_number, restaurant_name, language, store_location, opening_hours_string, timezone)
        if success:
            flash(f"You should receive the call on {phone_number} shortly.", 'success')
        else:
            flash("Something went wrong. Please try again.", 'danger')
        return redirect(url_for('voice_setup_page'))
    
    flash("Please fill out all required fields.", 'warning')
    return redirect(url_for('voice_setup_page'))

################### Voice Assistant Setup End #########################

    
######################### Chat Flow ############################

@app.route('/chat_start/<unique_azz_id>', methods=['GET', 'POST'])
def chat_start(unique_azz_id):
    iframe = True if request.args.get("iframe") else False
    print("Iframe we passed: ", iframe)
    
    assistant_id = collection.find_one({"unique_azz_id": unique_azz_id})["assistant_id"]
    return render_template("dashboard/choose_chat_lang.html", unique_azz_id=unique_azz_id, assistant_id=assistant_id, title="Start Chat", iframe=iframe)

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
    # tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
    )                                     

    session["current_thread_id"] = thread.id   

    print(f"Current thread id: {thread.id}")                                
    
    # Get current UTC time and format it as dd.mm hh:mm
    # timestamp_utc = datetime.utcnow().strftime('%d.%m.%Y %H:%M')
    # collection_threads.insert_one({"thread_id":thread.id, "restaurant_name":restaurant_name, "timestamp UTC":timestamp_utc})
    
    
    print(f"New thread created with ID: {thread.id}")  # Debugging line
    return jsonify({"thread_id": thread.id , "assistant_id": assistant_id})

@app.route('/assistant_order_chat/<unique_azz_id>/<current_thread_id>')
def assistant_order_chat(unique_azz_id, current_thread_id=None, from_splash_page=False):
    # Retrieve the full assistant_id from the session
    lang = request.args.get('lang', 'en')

    iframe = True if request.args.get("iframe") else False
    from_splash_page = True if request.args.get("from_splash_page") else False

    res_instance = collection.find_one({"unique_azz_id":unique_azz_id})

    full_assistant_id = res_instance.get("assistant_id")
    restaurant_name = res_instance.get("name")
    restaurant_website_url = res_instance.get("website_url")
    menu_file_id = res_instance.get("menu_file_id")
    menu_vector_id = res_instance.get("menu_vector_id")
    res_currency = res_instance.get("res_currency")
    current_balanceHigherThanTwentyCents = round(res_instance.get("balance"), 2) >= 0.2
    default_menu = False
    discovery_mode = res_instance.get("discovery_mode")
    menu_vector_id = res_instance.get("menu_vector_id")
    if menu_vector_id == MOM_AI_EXEMPLARY_MENU_VECTOR_ID:
        default_menu = True
    assistant_turned_on = res_instance.get("assistant_turned_on")
    print(f"Assistant turned on:{assistant_turned_on} of type {type(assistant_turned_on)}")

    # id_of_intro = res_instance.get("intro_video_id", "default_later_here")
    # intro_video_link = get_talk_video(id_of_intro)['result_url']

    # print("Intro video link we send", intro_video_link)
    
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
    # print(f"Current time in {timezone}: {now_tz}, Working hours for today: {start_work.get(current_day)} to {end_work[current_day]}, isWorkingHours: {isWorkingHours}")


    session["unique_azz_id"] = unique_azz_id
    session["full_assistant_id"] = full_assistant_id
    session["menu_file_id"] = menu_file_id
    session["menu_vector_id"] = menu_vector_id
    session["res_currency"] = res_currency
    session["restaurant_name"] = restaurant_name

    response = CLIENT_OPENAI.beta.threads.messages.list(current_thread_id)

    # print(response)

    # Define the regex pattern to capture the text after "Customer's message:"
    pattern = r"Customer's message:\s*(.*)"

    list_of_current_messages = []
    for chunk in response.data:
        message = {}
        message["role"] = chunk.role
        # Use re.search to find and extract the part after "Customer's message:"
        text_content = chunk.content[0].text.value
        message["content"] = text_content
        
        if chunk.role == "user":
            match = re.search(pattern, text_content)
            
            message["content"] = match.group(1)
        list_of_current_messages.append(message)
    
    runs = CLIENT_OPENAI.beta.threads.runs.list(
    current_thread_id
    )

    requires_action = False
    suggest_new_order = False
    
    # Iterate over runs.data and check if any status is "requires_action"
    for run in runs.data:
        if run.status == "requires_action":
            requires_action = True
            break  # Exit the loop early if "requires_action" is found

    if len(runs.data) > 0:
        # Get the current timestamp
        current_timestamp = time.time() 
        if current_timestamp - runs.data[-1].created_at > 300:
            suggest_new_order = True
        # print(f"List of current messages: {list_of_current_messages}")
        print(f"Suggest new order: {suggest_new_order} and requires action: {requires_action}")

    # Use the restaurant_name from the URL and the full assistant_id from the session
    return render_template('dashboard/order_chatSTREAMING.html', restaurant_name=restaurant_name, 
                           lang=lang, 
                           assistant_id=full_assistant_id, 
                           unique_azz_id=unique_azz_id, 
                           restaurant_website_url=restaurant_website_url, 
                           title=f"{restaurant_name}'s Assistant", 
                           assistant_turned_on=assistant_turned_on, 
                           restaurant=res_instance, 
                           iframe=iframe, 
                           isWorkingHours=isWorkingHours,
                           default_menu=default_menu,
                           discovery_mode=discovery_mode,
                           current_balanceHigherThanTwentyCents = current_balanceHigherThanTwentyCents,
                           from_splash_page=from_splash_page,
                           list_of_current_messages=list_of_current_messages,
                           requires_action=requires_action,
                           suggest_new_order=suggest_new_order)





@app.route('/assistant_order_chat_streaming/<unique_azz_id>')
def assistant_order_chat_streaming(unique_azz_id, from_splash_page=False):
    # Retrieve the full assistant_id from the session
    lang = request.args.get('lang', 'en')

    iframe = True if request.args.get("iframe") else False
    from_splash_page = True if request.args.get("from_splash_page") else False

    res_instance = collection.find_one({"unique_azz_id":unique_azz_id})

    full_assistant_id = res_instance.get("assistant_id")
    restaurant_name = res_instance.get("name")
    restaurant_website_url = res_instance.get("website_url")
    menu_file_id = res_instance.get("menu_file_id")
    menu_vector_id = res_instance.get("menu_vector_id")
    res_currency = res_instance.get("res_currency")
    current_balanceHigherThanTwentyCents = round(res_instance.get("balance"), 2) >= 0.2
    default_menu = False
    discovery_mode = res_instance.get("discovery_mode")
    menu_vector_id = res_instance.get("menu_vector_id")
    if menu_vector_id == MOM_AI_EXEMPLARY_MENU_VECTOR_ID:
        default_menu = True
    assistant_turned_on = res_instance.get("assistant_turned_on")
    print(f"Assistant turned on:{assistant_turned_on} of type {type(assistant_turned_on)}")

    # id_of_intro = res_instance.get("intro_video_id", "default_later_here")
    # intro_video_link = get_talk_video(id_of_intro)['result_url']

    # print("Intro video link we send", intro_video_link)
    
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
    # print(f"Current time in {timezone}: {now_tz}, Working hours for today: {start_work.get(current_day)} to {end_work[current_day]}, isWorkingHours: {isWorkingHours}")


    session["unique_azz_id"] = unique_azz_id
    session["full_assistant_id"] = full_assistant_id
    session["menu_file_id"] = menu_file_id
    session["menu_vector_id"] = menu_vector_id
    session["res_currency"] = res_currency
    session["restaurant_name"] = restaurant_name

    print("Discovery mode we passed: ", discovery_mode)
    # Use the restaurant_name from the URL and the full assistant_id from the session
    return render_template('dashboard/order_chatSTREAMING.html', restaurant_name=restaurant_name, 
                           lang=lang, 
                           assistant_id=full_assistant_id, 
                           unique_azz_id=unique_azz_id, 
                           restaurant_website_url=restaurant_website_url, 
                           title=f"{restaurant_name}'s Assistant", 
                           assistant_turned_on=assistant_turned_on, 
                           restaurant=res_instance, 
                           iframe=iframe, 
                           isWorkingHours=isWorkingHours,
                           default_menu=default_menu,
                           discovery_mode=discovery_mode,
                           current_balanceHigherThanTwentyCents = current_balanceHigherThanTwentyCents,
                           from_splash_page=from_splash_page)

from functions_to_use import c, get_assistants_response_streaming, MOM_AI_JSON_LORD_ID, transform_orders_to_string

@app.route('/generate_response_streaming/<unique_azz_id>', methods=['POST', 'GET'])
def generate_response_streaming(unique_azz_id):
    # Set the environment variable for Google Cloud credentials
    # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\Users\mmatr\AppData\Roaming\gcloud\application_default_credentials.json'
    

    restaurant_instance = collection.find_one({"unique_azz_id": unique_azz_id})
    payment_on = restaurant_instance.get("paymentGatewayTurnedOn")
    discovery_mode = restaurant_instance.get('discovery_mode')
    
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
    session_data = {}
    
    menu_file_id = restaurant_instance.get("menu_file_id")
    res_currency = restaurant_instance.get("res_currency")
    print(f"Menu file ID on /generate_response: {menu_file_id}")

    print(f"User input: {user_input}")
    print(f"Thread ID: {thread_id}")
    print(f"Assistant ID: {assistant_id}")

    html_menu_tuples = restaurant_instance.get('html_menu_tuples')

    for item in html_menu_tuples:
        if "Item Price (EUR)" in item:
            # Rename the key
            item["Item Price"] = item.pop("Item Price (EUR)")
    
    client = CLIENT_OPENAI
    
    stream = get_assistants_response_streaming(user_input, language, thread_id, assistant_id, menu_file_id, CLIENT_OPENAI, payment_on, list_of_all_items=html_menu_tuples, list_of_image_links=None, unique_azz_id=unique_azz_id, res_currency=res_currency, discovery_mode=discovery_mode)

    def generate():

        for chunk in stream:
            # print(chunk)
            
            if chunk.event == "thread.message.delta":
                print(f"\n\nYielding message delta content: {chunk.data.delta.content[0].text.value}\n\n")
                yield(chunk.data.delta.content[0].text.value)
            if chunk.event == "thread.run.completed":
                tokens_used = chunk.data.usage.total_tokens
                
                charge_for_message = PRICE_PER_1_TOKEN * tokens_used
                print(f"\n\nCharge for message in generate(): {charge_for_message} USD\n\n")

                result_charge_for_message = collection.update_one({"unique_azz_id": unique_azz_id}, {"$inc": {"balance": -charge_for_message, "assistant_fund": charge_for_message}})
                if result_charge_for_message.matched_count > 0:
                    print("Balances were successfully updated.")
                else:
                    print("No matching document found.")
            if chunk.event == "thread.run.requires_action":
                if discovery_mode:
                    print("Action interrupted because of discovery mode.")
                    run = client.beta.threads.runs.cancel(
                        thread_id=thread_id,
                        run_id=run.id
                        )
                    no_action_response = "Please, type in the other message as I can't proceed with the placement of the order. I am not entitled to do that."
                    print("Yielding discovery mode no order message: discovery_mode_no_order")
                    yield "discovery_mode_no_order"
                print("Action in progress...")

                if res_currency != 'EUR':
                    rate = c.convert(1, res_currency, 'EUR')
                else:
                    rate = 1
                
                messages_gpt = client.beta.threads.messages.list(thread_id=thread_id)
                #print(f"Messages retrieved in action step {messages_gpt}")  # debugging line

                joined_messages_of_assistant = ""
                messages_gpt_list = list(messages_gpt)
                messages_gpt_list.reverse()

                pattern = r"Task: Here is the current user's message, respond to it:\n\s*(.*?)\s*\(in the context of"
                
                for message in messages_gpt_list:
                    if message.role == 'assistant':
                        joined_messages_of_assistant += f"\nAssistant:\n{message.content[0].text.value}\n"
                    if message.role == 'user':
                        match = re.search(pattern, message.content[0].text.value, re.DOTALL)
                        if match:
                            user_message = match.group(1).strip()
                            joined_messages_of_assistant += f"\nCustomer:\n{user_message}\n"
                        else:
                            joined_messages_of_assistant += f"\nCustomer:\n{message.content[0].text.value}\n"

                print(f"\nRetrieved all messages with Summary from convo: {joined_messages_of_assistant}\n")

                summary_to_convert = f"""
                These are all messages of the assistant from the chat with client. 
                From the following messages find the last one which summarizes agreed upon order and retrieve items stated in the final confirmed summary:
                {joined_messages_of_assistant}
                Ensure that the found items are part of this list of items presented in the format (item name, item ingredients, item price):
                {html_menu_tuples}
                """

                print(f"Summary to convert sent to MOM AI JSON: {summary_to_convert}")  # debugging line
                

                thread_id_json = client.beta.threads.create().id
                print(f"JSON assistant thread {thread_id_json}")

                response = client.beta.threads.messages.create(thread_id=thread_id_json,
                                                            role="user",
                                                            content=summary_to_convert)

                run_json = client.beta.threads.runs.create(thread_id=thread_id_json,
                                                        assistant_id=MOM_AI_JSON_LORD_ID)

                json_start_time = time.time()
                while True:
                    if time.time() - json_start_time > 25:
                        response = 'O-oh, little issues when forming the response, repeat the message now'
                        print("Yielding message to write again: Please, write the message again!")
                        yield "Please, write the message again!"

                    run_status = client.beta.threads.runs.retrieve(thread_id=thread_id_json,
                                                                run_id=run_json.id)
                    if run_status.status == 'completed':
                        messages_gpt_json = client.beta.threads.messages.list(thread_id=thread_id_json)
                        print(f"\n\nTokens used by JSON assistant: {run_status.usage.total_tokens}\n\n")
                        total_tokens_used_JSON = run_status.usage.total_tokens
                        total_tokens_used = total_tokens_used_JSON

                        
                        charge_for_message = PRICE_PER_1_TOKEN * total_tokens_used
                        print(f"Charge for message in JSON generate(): {charge_for_message} USD")

                        result_charge_for_message = collection.update_one({"unique_azz_id": unique_azz_id}, {"$inc": {"balance": -charge_for_message, "assistant_fund": charge_for_message}})
                        if result_charge_for_message.matched_count > 0:
                            print("Balances were successfully updated.")
                        
                        formatted_json_order = messages_gpt_json.data[0].content[0].text.value
                        print(f"\nFormatted JSON Order (Output from MOM AI JSON LORD): {formatted_json_order}\n")

                        # Get the conversion rate from USD to EUR (you can change to any currencies)
                        
                        parsed_formatted_json_order = ast.literal_eval(formatted_json_order.strip())
                        items_ordered = parsed_formatted_json_order["items_ordered"]
                        cache.set("items_ordered", items_ordered)
                        # print(f"Setup the items ordered on assistant response! {parsed_formatted_json_order['items']}")
                    
                        order_id = generate_code()
                        current_utc_timestamp = time.time()

                        # Convert the timestamp to a datetime object
                        utc_datetime = datetime.utcfromtimestamp(current_utc_timestamp)

                        # Format the datetime object to a human-readable string
                        human_readable_time_format = utc_datetime.strftime('%Y-%m-%d %H:%M')


                        if items_ordered and payment_on:
                            db_items_cache[unique_azz_id].insert_one({"data": items_ordered, "id": order_id, "timestamp": current_utc_timestamp})

                        if payment_on:
                            total_price = f"{sum(item['quantity'] * item['price'] for item in items_ordered):.2f}"
                            
                            total_price_EUR = f"{float(total_price)*rate:.2f}"

                            cache.set("currency", res_currency)
                            cache.set("currency_rate", rate)

                            
                            link_to_payment_buffer = f"/payment_buffer/{unique_azz_id}/{order_id}"
                            print(link_to_payment_buffer)

                            clickable_link = f'<a href={link_to_payment_buffer} style="color: #c0c0c0;" target="_blank">Press here to proceed</a>'
                            response_cart = f"Order formed successfully. Please, follow this link to finish the purchase: {clickable_link}"
                            # translator.translate()

                            # Charge acc with 'total_tokens_used'

                            print(f"Yielding link to payment buffer: {link_to_payment_buffer}")
                            yield link_to_payment_buffer
                        else:
                            total_price = f"{sum(item['quantity'] * item['price'] for item in items_ordered):.2f}"

                            
                            total_price_EUR = f"{float(total_price)*rate:.2f}"

                            cache.set("currency", res_currency)
                            cache.set("currency_rate", rate)

                            cache.set("total_price_EUR", total_price_EUR)
                            cache.set("total_price_NATIVE", total_price)

                            cache.set("order_id", order_id)
                            cache.set("access_granted_no_payment_order", True)

                            """
                            order_to_pass = {"items":[{'name':item['name'], 'quantity':item['quantity']} for item in items_ordered], 
                            "orderID":order_id,
                            "timestamp": human_readable_time_format,
                            "total_paid": total_price,
                            "total_paid_EUR": total_price_EUR,
                            "mom_ai_restaurant_assistant_fee": 0,
                            "paypal_fee": 0,
                            "paid":"NOT PAID",
                            "published":True}
        
                            db_order_dashboard[unique_azz_id].insert_one(order_to_pass)
                            # print("\n\nInserted the order in db_order_dashboard with if ", unique_azz_id, "\n\n")
                            """
                            
                            string_of_items = transform_orders_to_string(items_ordered)

                            no_payment_order_finish_message = f"Thank you very much! You ordered {string_of_items} and total is {total_price} {res_currency}\nCome to the restaurant and pick up your meal shortly. Love💖\n**PLEASE SAVE THIS: Your order ID is {order_id}**"
                            
                            restaurant_instance = collection.find_one({"unique_azz_id":unique_azz_id})
                            all_ids_chats = restaurant_instance.get("notif_destin", [])

                            cache.set("order_confirm_access_granted", True)
                            
                            for chat_id in all_ids_chats:
                                send_telegram_notification(chat_id)
                            cache.set("suggest_web3_bonus", True)

                            # Charge acc with 'total_tokens_used'

                            print(f"Yielding no payment order finish message: {no_payment_order_finish_message}")
                            yield no_payment_order_finish_message
                    if run_status.status == 'failed':
                        print("Run of JSON assistant failed.")
                        last_error = run_json.last_error if "last_error" in run else None
                        if last_error:
                            print("Last Error:", last_error)
                        else:
                            print("No errors reported for this run.")

                        #print(f"\n\nRun steps: \n{run_steps}\n")
                        response = 'O-oh, little issues, repeat the message now'
                        print("Yielding message to write again: Please, write the message again!")
                        yield "Please, write the message again!"
    
    for key, value in session_data.items():
        session[key] = value

    return Response(generate(), content_type='text/plain')

"""
import pyaudio
p = pyaudio.PyAudio()
stream = p.open(format=8,
                channels=1,
                rate=24_000,
                output=True)
"""
@app.route('/generate_voice_output_ONLY_VOICE_streaming/<unique_azz_id>', methods=['POST'])
def generate_response_VOICE_ONLY_streaming(unique_azz_id):
    restaurant_instance = collection.find_one({"unique_azz_id": unique_azz_id})
    payment_on = restaurant_instance.get("paymentGatewayTurnedOn")
    discovery_mode = restaurant_instance.get('discovery_mode')
    
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
    session_data = {}
    
    menu_file_id = restaurant_instance.get("menu_file_id")
    res_currency = restaurant_instance.get("res_currency")
    print(f"Menu file ID on /generate_response: {menu_file_id}")

    print(f"User input: {user_input}")
    print(f"Thread ID: {thread_id}")
    print(f"Assistant ID: {assistant_id}")

    html_menu_tuples = restaurant_instance.get('html_menu_tuples')

    for item in html_menu_tuples:
        if "Item Price (EUR)" in item:
            # Rename the key
            item["Item Price"] = item.pop("Item Price (EUR)")
    
    client = CLIENT_OPENAI

    def generate():
        stream = get_assistants_response_celery_VOICE_ONLY_streaming(user_input, language, thread_id, assistant_id, menu_file_id, payment_on, list_of_all_items=html_menu_tuples, list_of_image_links=None, unique_azz_id=unique_azz_id, res_currency=res_currency, discovery_mode=discovery_mode)
        
        sentence = ""
        
        # Define sentence-ending punctuation marks
        sentence_endings = re.compile(r'[.!?]')

        # Adjusting buffer size limits
        BUFFER_LIMIT = 200  # Adjust to control when to send mid-sentence
        
        for chunk in stream:
            if chunk.event == "thread.message.delta":
                text_chunk = chunk.data.delta.content[0].text.value
                sentence += text_chunk  # Append to the sentence

                # Once a sentence is complete or large enough, send it for TTS
                if sentence_endings.search(sentence):
                    try:
                        # Call TTS API and stream audio chunks back
                        with client.audio.speech.with_streaming_response.create(
                            model="tts-1-hd",
                            voice="nova",
                            input=sentence,
                            speed=1.2,
                            response_format="pcm"
                        ) as response:
                            for audio_chunk in response.iter_bytes(1024):
                                yield audio_chunk  # Stream audio to the client
                        
                        sentence = ""  # Reset sentence after processing

                    except Exception as e:
                        print(f"Error generating audio: {e}")
                        yield b"Error processing the sentence."
            elif chunk.event == "thread.run.failed":
                yield ("Error in Thread")
            elif chunk.event == "thread.run.requires_action":
                if discovery_mode:
                    print("Action interrupted because of discovery mode.")
                    run = client.beta.threads.runs.cancel(
                        thread_id=thread_id,
                        run_id=run.id
                        )
                    no_action_response = "Please, type in the other message as I can't proceed with the placement of the order. I am not entitled to do that."
                    yield "discovery_mode_no_order"
                print("Action in progress...")

                messages_gpt = client.beta.threads.messages.list(thread_id=thread_id)
                #print(f"Messages retrieved in action step {messages_gpt}")  # debugging line

                joined_messages_of_assistant = ""
                messages_gpt_list = list(messages_gpt)
                messages_gpt_list.reverse()

                pattern = r"Task: Here is the current user's message, respond to it:\n\s*(.*?)\s*\(in the context of"
                
                for message in messages_gpt_list:
                    if message.role == 'assistant':
                        joined_messages_of_assistant += f"\nAssistant:\n{message.content[0].text.value}\n"
                    if message.role == 'user':
                        match = re.search(pattern, message.content[0].text.value, re.DOTALL)
                        if match:
                            user_message = match.group(1).strip()
                            joined_messages_of_assistant += f"\nCustomer:\n{user_message}\n"
                        else:
                            joined_messages_of_assistant += f"\nCustomer:\n{message.content[0].text.value}\n"

                print(f"\nRetrieved all messages with Summary from convo: {joined_messages_of_assistant}\n")

                summary_to_convert = f"""
                These are all messages of the assistant from the chat with client. 
                From the following messages find the last one which summarizes agreed upon order and retrieve items stated in the final confirmed summary:
                {joined_messages_of_assistant}
                Ensure that the found items are part of this list of items presented in the format (item name, item ingredients, item price):
                {html_menu_tuples}
                """

                print(f"Summary to convert sent to MOM AI JSON: {summary_to_convert}")  # debugging line
                

                thread_id_json = client.beta.threads.create().id
                print(f"JSON assistant thread {thread_id_json}")

                response = client.beta.threads.messages.create(thread_id=thread_id_json,
                                                            role="user",
                                                            content=summary_to_convert)

                run_json = client.beta.threads.runs.create(thread_id=thread_id_json,
                                                        assistant_id=MOM_AI_JSON_LORD_ID)

                json_start_time = time.time()
                while True:
                    if time.time() - json_start_time > 25:
                        response = 'O-oh, little issues when forming the response, repeat the message now'
                        yield "Please, write the message again!"

                    run_status = client.beta.threads.runs.retrieve(thread_id=thread_id_json,
                                                                run_id=run_json.id)
                    if run_status.status == 'completed':
                        messages_gpt_json = client.beta.threads.messages.list(thread_id=thread_id_json)
                        print(f"\n\nTokens used by JSON assistant: {run_status.usage.total_tokens}\n\n")
                        total_tokens_used_JSON = run_status.usage.total_tokens
                        total_tokens_used = total_tokens_used_JSON

                        if res_currency != 'EUR':
                            rate = c.convert(1, res_currency, 'EUR')
                        else:
                            rate = 1
                        
                        charge_for_message = PRICE_PER_1_TOKEN * total_tokens_used
                        print(f"Charge for message in JSON generate(): {charge_for_message} USD")

                        result_charge_for_message = collection.update_one({"unique_azz_id": unique_azz_id}, {"$inc": {"balance": -charge_for_message, "assistant_fund": charge_for_message}})
                        if result_charge_for_message.matched_count > 0:
                            print("Balances were successfully updated.")
                        
                        formatted_json_order = messages_gpt_json.data[0].content[0].text.value
                        print(f"\nFormatted JSON Order (Output from MOM AI JSON LORD): {formatted_json_order}\n")

                        # Get the conversion rate from USD to EUR (you can change to any currencies)
                        
                        parsed_formatted_json_order = ast.literal_eval(formatted_json_order.strip())
                        items_ordered = parsed_formatted_json_order["items_ordered"]
                        cache.set("items_ordered", items_ordered)
                        # print(f"Setup the items ordered on assistant response! {parsed_formatted_json_order['items']}")
                    
                        order_id = generate_code()
                        current_utc_timestamp = time.time()

                        # Convert the timestamp to a datetime object
                        utc_datetime = datetime.utcfromtimestamp(current_utc_timestamp)

                        # Format the datetime object to a human-readable string
                        human_readable_time_format = utc_datetime.strftime('%Y-%m-%d %H:%M')


                        if items_ordered and payment_on:
                            db_items_cache[unique_azz_id].insert_one({"data": items_ordered, "id": order_id, "timestamp": current_utc_timestamp})

                        if payment_on:
                            total_price = f"{sum(item['quantity'] * item['price'] for item in items_ordered):.2f}"
                            
                            total_price_EUR = f"{float(total_price)*rate:.2f}"

                            cache.set("currency", res_currency)
                            cache.set("currency_rate", rate)

                            
                            link_to_payment_buffer = f"/payment_buffer/{unique_azz_id}/{order_id}"
                            print(link_to_payment_buffer)

                            clickable_link = f'<a href={link_to_payment_buffer} style="color: #c0c0c0;" target="_blank">Press here to proceed</a>'
                            response_cart = f"Order formed successfully. Please, follow this link to finish the purchase: {clickable_link}"
                            # translator.translate()

                            # Charge acc with 'total_tokens_used'

                            yield link_to_payment_buffer
                        else:
                            total_price = f"{sum(item['quantity'] * item['price'] for item in items_ordered):.2f}"
                            
                            
                            
                            total_price_EUR = f"{float(total_price)*rate:.2f}"

                            cache.set("currency", res_currency)
                            cache.set("currency_rate", rate)

                            cache.set("total_price_EUR", total_price_EUR)
                            cache.set("total_price_NATIVE", total_price)

                            cache.set("order_id", order_id)
                            cache.set('access_granted_no_payment_order', True)

                            order_to_pass = {"items":[{'name':item['name'], 'quantity':item['quantity']} for item in items_ordered], 
                            "orderID":order_id,
                            "timestamp": human_readable_time_format,
                            "total_paid": total_price,
                            "total_paid_EUR": total_price_EUR,
                            "mom_ai_restaurant_assistant_fee": 0,
                            "paypal_fee": 0,
                            "paid":"NOT PAID",
                            "published":True}
        
                            db_order_dashboard[unique_azz_id].insert_one(order_to_pass)
                            # print("\n\nInserted the order in db_order_dashboard with if ", unique_azz_id, "\n\n")
                            
                            string_of_items = transform_orders_to_string(items_ordered)

                            no_payment_order_finish_message = f"Thank you very much! You ordered {string_of_items} and total is {total_price} {res_currency}\nCome to the restaurant and pick up your meal shortly. Love💖\n**PLEASE SAVE THIS: Your order ID is {order_id}**"
                            
                            restaurant_instance = collection.find_one({"unique_azz_id":unique_azz_id})
                            all_ids_chats = restaurant_instance.get("notif_destin", [])

                            cache.set("order_confirm_access_granted", True)
                            
                            for chat_id in all_ids_chats:
                                send_telegram_notification(chat_id)
                            cache.set("suggest_web3_bonus", True)

                            # Charge acc with 'total_tokens_used'

                            yield no_payment_order_finish_message
                    if run_status.status == 'failed':
                        print("Run of JSON assistant failed.")
                        last_error = run_json.last_error if "last_error" in run else None
                        if last_error:
                            print("Last Error:", last_error)
                        else:
                            print("No errors reported for this run.")

                        #print(f"\n\nRun steps: \n{run_steps}\n")
                        response = 'O-oh, little issues, repeat the message now'
                        yield "Please, write the message again!"
            
            # Ensure any remaining text is processed
        if sentence:
            with client.audio.speech.with_streaming_response.create(
                model="tts-1-hd",
                voice="nova",
                input=sentence,
                speed=1.2,
                response_format="wav"
            ) as response:
                for audio_chunk in response.iter_bytes(1024):
                    print("Audio Chunk: ", audio_chunk)
                    yield audio_chunk
    
    for key, value in session_data.items():
        session[key] = value

    return Response(generate(), content_type='audio/wav')

# Directory where speech files are stored
speech_dir = Path(__file__).parent

# Function to generate dynamic file names
def get_dynamic_speech_file_name():
    # List all files in the directory that match the pattern 'speech*.mp3'
    existing_files = list(speech_dir.glob('speech*.mp3'))

    # Get the highest number from the existing files, or start at 1 if no files exist
    if existing_files:
        # Extract the numeric part of the file names
        max_num = max([int(file.stem.replace('speech', '')) for file in existing_files if file.stem.replace('speech', '').isdigit()])
        next_file_num = max_num + 1
    else:
        next_file_num = 1

    # Create the new file name
    return speech_dir / f"speech{next_file_num}.mp3"










from flask_socketio import emit




@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")




@socketio.on('start_audio_stream')
def handle_start_audio_stream(data):
    print("start_audio_stream event received:", data)
    unique_azz_id = data.get('unique_azz_id')
    user_input = data.get('message', '')
    thread_id = data.get('thread_id')
    assistant_id = data.get('assistant_id')
    language = data.get("language", "en-US")[:2]
    
    restaurant_instance = collection.find_one({"unique_azz_id": unique_azz_id})
    payment_on = restaurant_instance.get("paymentGatewayTurnedOn")
    discovery_mode = restaurant_instance.get('discovery_mode')
    
    print("\n\nlanguage we received on /generate_response: ", language, "\n\n")
    
    transcription = " "

    restaurant_instance = collection.find_one({"unique_azz_id": unique_azz_id})
    session_data = {}
    
    menu_file_id = restaurant_instance.get("menu_file_id")
    res_currency = restaurant_instance.get("res_currency")
    print(f"Menu file ID on /generate_response: {menu_file_id}")

    print(f"User input: {user_input}")
    print(f"Thread ID: {thread_id}")
    print(f"Assistant ID: {assistant_id}")

    html_menu_tuples = restaurant_instance.get('html_menu_tuples')

    for item in html_menu_tuples:
        if "Item Price (EUR)" in item:
            # Rename the key
            item["Item Price"] = item.pop("Item Price (EUR)")
    
    client = CLIENT_OPENAI

    stream = get_assistants_response_celery_VOICE_ONLY_streaming(user_input, language, thread_id, assistant_id, menu_file_id,
                                                                 payment_on, list_of_all_items=html_menu_tuples, 
                                                                 list_of_image_links=None, unique_azz_id=unique_azz_id, 
                                                                 res_currency=res_currency, discovery_mode=discovery_mode)
    
    sentence = ""
    
    # Define sentence-ending punctuation marks
    sentence_endings = re.compile(r'[.!?]')

    # Adjusting buffer size limits
    BUFFER_LIMIT = 200  # Adjust to control when to send mid-sentence
    
    for chunk in stream:
        if chunk.event == "thread.message.delta":
            text_chunk = chunk.data.delta.content[0].text.value
            sentence += text_chunk  # Append to the sentence

            # Once a sentence is complete or large enough, send it for TTS
            if len(sentence)>BUFFER_LIMIT or sentence_endings.search(sentence):
                try:
                    threading.Thread(target=stream_audio, args=(sentence)).start()
                    
                    sentence = ""  # Reset sentence after processing

                except Exception as e:
                    print(f"Error generating audio: {e}")
                    emit('error', {'message': 'Error processing the sentence.'})
        elif chunk.event == "thread.run.failed":
            socketio.emit('error', {'message': 'Error in Thread'})
        elif chunk.event == "thread.run.requires_action":
            if discovery_mode:
                print("Action interrupted because of discovery mode.")
                run = client.beta.threads.runs.cancel(
                    thread_id=thread_id,
                    run_id=run.id
                    )
                no_action_response = "Please, type in the other message as I can't proceed with the placement of the order. I am not entitled to do that."
                emit('discovery_mode_no_order', {'message': 'Order cannot proceed due to discovery mode.'})
            print("Action in progress...")

            messages_gpt = client.beta.threads.messages.list(thread_id=thread_id)
            #print(f"Messages retrieved in action step {messages_gpt}")  # debugging line

            joined_messages_of_assistant = ""
            messages_gpt_list = list(messages_gpt)
            messages_gpt_list.reverse()

            pattern = r"Task: Here is the current user's message, respond to it:\n\s*(.*?)\s*\(in the context of"
            
            for message in messages_gpt_list:
                if message.role == 'assistant':
                    joined_messages_of_assistant += f"\nAssistant:\n{message.content[0].text.value}\n"
                if message.role == 'user':
                    match = re.search(pattern, message.content[0].text.value, re.DOTALL)
                    if match:
                        user_message = match.group(1).strip()
                        joined_messages_of_assistant += f"\nCustomer:\n{user_message}\n"
                    else:
                        joined_messages_of_assistant += f"\nCustomer:\n{message.content[0].text.value}\n"

            print(f"\nRetrieved all messages with Summary from convo: {joined_messages_of_assistant}\n")

            summary_to_convert = f"""
            These are all messages of the assistant from the chat with client. 
            From the following messages find the last one which summarizes agreed upon order and retrieve items stated in the final confirmed summary:
            {joined_messages_of_assistant}
            Ensure that the found items are part of this list of items presented in the format (item name, item ingredients, item price):
            {html_menu_tuples}
            """

            print(f"Summary to convert sent to MOM AI JSON: {summary_to_convert}")  # debugging line
            

            thread_id_json = client.beta.threads.create().id
            print(f"JSON assistant thread {thread_id_json}")

            response = client.beta.threads.messages.create(thread_id=thread_id_json,
                                                        role="user",
                                                        content=summary_to_convert)

            run_json = client.beta.threads.runs.create(thread_id=thread_id_json,
                                                    assistant_id=MOM_AI_JSON_LORD_ID)

            json_start_time = time.time()
            while True:
                if time.time() - json_start_time > 25:
                    response = 'O-oh, little issues when forming the response, repeat the message now'
                    yield "Please, write the message again!"

                run_status = client.beta.threads.runs.retrieve(thread_id=thread_id_json,
                                                            run_id=run_json.id)
                if run_status.status == 'completed':
                    messages_gpt_json = client.beta.threads.messages.list(thread_id=thread_id_json)
                    print(f"\n\nTokens used by JSON assistant: {run_status.usage.total_tokens}\n\n")
                    total_tokens_used_JSON = run_status.usage.total_tokens
                    total_tokens_used = total_tokens_used_JSON

                    if res_currency != 'EUR':
                        rate = c.convert(1, res_currency, 'EUR')
                    else:
                        rate = 1
                    
                    charge_for_message = PRICE_PER_1_TOKEN * total_tokens_used
                    print(f"Charge for message in JSON generate(): {charge_for_message} USD")

                    result_charge_for_message = collection.update_one({"unique_azz_id": unique_azz_id}, {"$inc": {"balance": -charge_for_message, "assistant_fund": charge_for_message}})
                    if result_charge_for_message.matched_count > 0:
                        print("Balances were successfully updated.")
                    
                    formatted_json_order = messages_gpt_json.data[0].content[0].text.value
                    print(f"\nFormatted JSON Order (Output from MOM AI JSON LORD): {formatted_json_order}\n")

                    # Get the conversion rate from USD to EUR (you can change to any currencies)
                    
                    parsed_formatted_json_order = ast.literal_eval(formatted_json_order.strip())
                    items_ordered = parsed_formatted_json_order["items_ordered"]
                    cache.set("items_ordered", items_ordered)
                    # print(f"Setup the items ordered on assistant response! {parsed_formatted_json_order['items']}")
                
                    order_id = generate_code()
                    current_utc_timestamp = time.time()

                    # Convert the timestamp to a datetime object
                    utc_datetime = datetime.utcfromtimestamp(current_utc_timestamp)

                    # Format the datetime object to a human-readable string
                    human_readable_time_format = utc_datetime.strftime('%Y-%m-%d %H:%M')


                    if items_ordered and payment_on:
                        db_items_cache[unique_azz_id].insert_one({"data": items_ordered, "id": order_id, "timestamp": current_utc_timestamp})

                    if payment_on:
                        total_price = f"{sum(item['quantity'] * item['price'] for item in items_ordered):.2f}"
                        
                        total_price_EUR = f"{float(total_price)*rate:.2f}"

                        cache.set("currency", res_currency)
                        cache.set("currency_rate", rate)

                        
                        link_to_payment_buffer = f"/payment_buffer/{unique_azz_id}/{order_id}"
                        print(link_to_payment_buffer)

                        clickable_link = f'<a href={link_to_payment_buffer} style="color: #c0c0c0;" target="_blank">Press here to proceed</a>'
                        response_cart = f"Order formed successfully. Please, follow this link to finish the purchase: {clickable_link}"
                        # translator.translate()

                        # Charge acc with 'total_tokens_used'

                        emit(link_to_payment_buffer)
                    else:
                        total_price = f"{sum(item['quantity'] * item['price'] for item in items_ordered):.2f}"
                        
                        
                        
                        total_price_EUR = f"{float(total_price)*rate:.2f}"

                        cache.set("currency", res_currency)
                        cache.set("currency_rate", rate)

                        cache.set("total_price_EUR", total_price_EUR)
                        cache.set("total_price_NATIVE", total_price)

                        cache.set("order_id", order_id)
                        cache.set('access_granted_no_payment_order', True)

                        order_to_pass = {"items":[{'name':item['name'], 'quantity':item['quantity']} for item in items_ordered], 
                        "orderID":order_id,
                        "timestamp": human_readable_time_format,
                        "total_paid": total_price,
                        "total_paid_EUR": total_price_EUR,
                        "mom_ai_restaurant_assistant_fee": 0,
                        "paypal_fee": 0,
                        "paid":"NOT PAID",
                        "published":True}
    
                        db_order_dashboard[unique_azz_id].insert_one(order_to_pass)
                        # print("\n\nInserted the order in db_order_dashboard with if ", unique_azz_id, "\n\n")
                        
                        string_of_items = transform_orders_to_string(items_ordered)

                        no_payment_order_finish_message = f"Thank you very much! You ordered {string_of_items} and total is {total_price} {res_currency}\nCome to the restaurant and pick up your meal shortly. Love💖\n**PLEASE SAVE THIS: Your order ID is {order_id}**"
                        
                        restaurant_instance = collection.find_one({"unique_azz_id":unique_azz_id})
                        all_ids_chats = restaurant_instance.get("notif_destin", [])

                        cache.set("order_confirm_access_granted", True)
                        
                        for chat_id in all_ids_chats:
                            send_telegram_notification(chat_id)
                        cache.set("suggest_web3_bonus", True)

                        # Charge acc with 'total_tokens_used'

                        emit(no_payment_order_finish_message)
                if run_status.status == 'failed':
                    print("Run of JSON assistant failed.")
                    last_error = run_json.last_error if "last_error" in run else None
                    if last_error:
                        print("Last Error:", last_error)
                    else:
                        print("No errors reported for this run.")

                    #print(f"\n\nRun steps: \n{run_steps}\n")
                    response = 'O-oh, little issues, repeat the message now'
                    emit('Please, write the message again!')
            
            # Ensure any remaining text is processed
        if sentence:
            try:
                with client.audio.speech.with_streaming_response.create(
                    model="tts-1-hd",
                    voice="nova",
                    input=sentence,
                    speed=1.2,
                    response_format="pcm"
                ) as response:
                    for audio_chunk in response.iter_bytes(1024):
                        print("Audio Chunk: ", audio_chunk)
                        emit('audio_chunk', audio_chunk)
            except Exception as e:
                print(f"Error generating remaining audio: {e}")
                emit('error', {'message': 'Error processing remaining text.'})
        
        # Notify the client that the stream has ended
        emit('audio_stream_end')


def stream_audio(sentence):
    try:
        with CLIENT_OPENAI.audio.speech.with_streaming_response.create(
            model="tts-1-hd", voice="nova", input=sentence, speed=1.2, response_format="pcm"
        ) as response:
            for audio_chunk in response.iter_bytes(1024):
                emit('audio_chunk', audio_chunk)
    except Exception as e:
        emit('error', {'message': 'Audio generation failed'})


@socketio.on('test')
def socket_test(data):
    name = data.get('name')

    print("\n\n\ncalled_test\n\n\n")
    emit("test_response", f"Hi, {name}")



















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
        
        # print(f"The phrase we transcribed: {result["transcription"]}")
        
        return jsonify(result)
    except Exception as e:
        print(f"Error during transcription: {e}")
        return jsonify({"error": str(e), "status": "fail"})






@app.route('/assistant_order_chat_VOICE_ONLY/<unique_azz_id>')
def assistant_order_chat_VOICE_ONLY(unique_azz_id, from_splash_page=False):
    # Retrieve the full assistant_id from the session
    lang = request.args.get('lang', 'en')

    iframe = True if request.args.get("iframe") else False
    from_splash_page = True if request.args.get("from_splash_page") else False

    res_instance = collection.find_one({"unique_azz_id":unique_azz_id})

    full_assistant_id = res_instance.get("assistant_id")
    restaurant_name = res_instance.get("name")
    restaurant_website_url = res_instance.get("website_url")
    menu_file_id = res_instance.get("menu_file_id")
    menu_vector_id = res_instance.get("menu_vector_id")
    res_currency = res_instance.get("res_currency")
    current_balanceHigherThanTwentyCents = round(res_instance.get("balance"), 2) >= 0.2
    default_menu = False
    discovery_mode = res_instance.get("discovery_mode")
    menu_vector_id = res_instance.get("menu_vector_id")
    if menu_vector_id == MOM_AI_EXEMPLARY_MENU_VECTOR_ID:
        default_menu = True
    assistant_turned_on = res_instance.get("assistant_turned_on")
    print(f"Assistant turned on:{assistant_turned_on} of type {type(assistant_turned_on)}")

    # id_of_intro = res_instance.get("intro_video_id", "default_later_here")
    # intro_video_link = get_talk_video(id_of_intro)['result_url']

    # print("Intro video link we send", intro_video_link)
    
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
    # print(f"Current time in {timezone}: {now_tz}, Working hours for today: {start_work.get(current_day)} to {end_work[current_day]}, isWorkingHours: {isWorkingHours}")


    session["unique_azz_id"] = unique_azz_id
    session["full_assistant_id"] = full_assistant_id
    session["menu_file_id"] = menu_file_id
    session["menu_vector_id"] = menu_vector_id
    session["res_currency"] = res_currency
    session["restaurant_name"] = restaurant_name

    print("Discovery mode we passed: ", discovery_mode)
    # Use the restaurant_name from the URL and the full assistant_id from the session
    return render_template('dashboard/order_chat_VOICE_ONLY.html', restaurant_name=restaurant_name, 
                           lang=lang, 
                           assistant_id=full_assistant_id, 
                           unique_azz_id=unique_azz_id, 
                           restaurant_website_url=restaurant_website_url, 
                           title=f"{restaurant_name}'s Assistant", 
                           assistant_turned_on=assistant_turned_on, 
                           restaurant=res_instance, 
                           iframe=iframe, 
                           isWorkingHours=isWorkingHours,
                           default_menu=default_menu,
                           discovery_mode=discovery_mode,
                           current_balanceHigherThanTwentyCents = current_balanceHigherThanTwentyCents,
                           from_splash_page=from_splash_page)






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

    _, tokens_used, video_url = generate_short_voice_output(full_gpts_response, language_to_translate_into)
    
    speech_file_path = Path(__file__).parent / "speech.mp3"

    charge_for_message = PRICE_PER_1_TOKEN * tokens_used
    print(f"Charge for message: {charge_for_message} USD")

    result_charge_for_message = collection.update_one({"unique_azz_id": unique_azz_id}, {"$inc": {"balance": -charge_for_message, "assistant_fund": charge_for_message}})
    if result_charge_for_message.matched_count > 0:
        print("Balances were successfully updated.")
    else:
        print("No matching document found.")

    print(f"\n\n\nVideo URL: {video_url}\n\n\n")

    # Return JSON with video URL and path for audio file
    return jsonify({
        "video_url": video_url,
        "audio_file_url": "/download_audio"
    })




@app.route('/generate_voice_output_streaming/<unique_azz_id>', methods=["POST", "GET"])
def generate_voice_output_STREAMING(unique_azz_id):
    client = CLIENT_OPENAI
    
    print("\n\n\n\n\n", "Triggered generate_voice_output_STREAMING", "\n\n\n\n\n")

    data = request.form
    full_gpts_response = data.get("full_gpts_response")
    language_to_translate_into = data.get("language")
    
    stream = generate_short_voice_output_streaming(full_gpts_response, language_to_translate_into)
    
    def generate():

        for chunk in stream:
            print("\n\n\n\n\n", chunk, "\n\n\n\n\n")
            
            print(f"\n\n\n\n\nYielded: {chunk.choices[0].delta.content}\n\n\n\n\n")
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content.encode('utf-8')
            else:
                yield ""
    return Response(generate(), content_type='text/plain')





@app.route('/generate_ONLY_VOICE_output/<unique_azz_id>', methods=["POST", "GET"])
def generate_voice_output_ONLY_VOICE(unique_azz_id):
    client = CLIENT_OPENAI
    
    data = request.form
    full_gpts_response = data.get("response_text")
    language_to_translate_into = data.get("language")

    generate_short_voice_output_VOICE_ONLY(unique_azz_id, full_gpts_response, language_to_translate_into)

    # Return JSON with video URL and path for audio file
    return jsonify({
        "audio_file_url": "/download_audio"
    })



@app.route('/generate_voice_output_VOICE_ONLY/<unique_azz_id>', methods=["POST", "GET"])
def generate_voice_output_VOICE_ONLY(unique_azz_id):
    client = CLIENT_OPENAI
    
    data = request.form
    full_gpts_response = data.get("full_gpts_response")
    language_to_translate_into = data.get("language")

    restaurant_instance = collection.find_one({"unique_azz_id": unique_azz_id})
    html_menu_tuples = restaurant_instance.get('html_menu_tuples')

    _, tokens_used, video_url = generate_short_voice_output_VOICE_ONLY(full_gpts_response, language_to_translate_into, html_menu_tuples)
    
    speech_file_path = Path(__file__).parent / "speech.mp3"

    

    charge_for_message = PRICE_PER_1_TOKEN * tokens_used
    print(f"Charge for message: {charge_for_message} USD")

    result_charge_for_message = collection.update_one({"unique_azz_id": unique_azz_id}, {"$inc": {"balance": -charge_for_message, "assistant_fund": charge_for_message}})
    if result_charge_for_message.matched_count > 0:
        print("Balances were successfully updated.")
    else:
        print("No matching document found.")

    print(f"\n\n\nVideo URL: {video_url}\n\n\n")

    # Return JSON with video URL and path for audio file
    return jsonify({
        "video_url": video_url,
        "audio_file_url": "/download_audio"
    })

@app.route('/download_audio', methods=["POST", "GET"])
def download_audio():
    # Get the audio file index from the query parameters (default is '1' if not provided)
    audio_index = request.args.get('audio_index')

    if audio_index:
        filename = f"speech{audio_index}.mp3"
    else:
        filename = "speech.mp3"
    # Construct the dynamic file path (e.g., speech1.mp3, speech2.mp3, etc.)
    speech_file_path = Path(__file__).parent / filename

    # Debugging: Print the constructed file path and check if it exists
    print(f"Attempting to access file: {speech_file_path}")
    
    # Check if the file exists
    if not speech_file_path.is_file():
        print(f"File not found: {speech_file_path}")  # Debugging: Log if the file is not found
        return "Audio file not found", 404

    print(f"File found: {speech_file_path}")  # Debugging: Log if the file is found

    return send_file(
        speech_file_path,
        mimetype='audio/mpeg',
        as_attachment=True,
        download_name=f'speech{audio_index}.mp3'
    )



@app.route('/delete_speeches', methods=['DELETE'])
def delete_speeches():
    speech_dir = Path(__file__).parent  # The directory where speech files are stored
    deleted_files = []

    # Find all files that match the pattern 'speech*.mp3'
    for speech_file in speech_dir.glob('speech*.mp3'):
        try:
            os.remove(speech_file)  # Delete the file
            deleted_files.append(speech_file.name)
        except OSError as e:
            return jsonify({"error": f"Failed to delete {speech_file.name}: {str(e)}"}), 500

    return jsonify({"message": "All speech files deleted", "deleted_files": deleted_files}), 200




### Celery Integration ###
@app.route('/trigger_generate_response/<unique_azz_id>', methods=['POST'])
def trigger_generate_response(unique_azz_id):
    data = request.form
    print(data)
    user_message = data.get('message', '')
    thread_id = data.get('thread_id')
    assistant_id = data.get('assistant_id')
    language = data.get("language", "en-US")[:2]

    # Retrieve other parameters
    restaurant_instance = collection.find_one({"unique_azz_id": unique_azz_id})
    payment_on = restaurant_instance.get("paymentGatewayTurnedOn")
    discovery_mode = restaurant_instance.get('discovery_mode')
    menu_file_id = restaurant_instance.get("menu_file_id")
    res_currency = restaurant_instance.get("res_currency")
    html_menu_tuples = restaurant_instance.get('html_menu_tuples')
    
    # Default image URL if no link is available
    default_image_url = "https://png.pngtree.com/png-vector/20221125/ourmid/pngtree-no-image-available-icon-flatvector-illustration-pic-design-profile-vector-png-image_40966566.jpg"

    # Iterate over each item in the 'html_menu_tuples' list
    for item in html_menu_tuples:
        # Step 1: Check if "Link to Image" is empty
        if not item.get('Link to Image'):
            # Step 2: If "Link to Image" is empty, check if "AI-Image" exists
            if item.get('AI-Image'):
                # Assign the AI image URL to "Link to Image"
                item['Link to Image'] = item['AI-Image']
                # Remove the 'AI-Image' field after assigning its value
                del item['AI-Image']
            else:
                # Step 3: If "AI-Image" does not exist, assign the default image URL
                item['Link to Image'] = default_image_url
    
    list_of_image_links = None  # Set or retrieve if necessary

    print("\n\n\n", html_menu_tuples, "\n\n\n")

    # Trigger the asynchronous task
    task = get_assistants_response_celery.apply_async(
        args=[
            user_message, language, thread_id, assistant_id, menu_file_id, 
            payment_on, html_menu_tuples, list_of_image_links, unique_azz_id, res_currency, discovery_mode
        ]
    )

    return jsonify({"task_id": task.id}), 202  # Return task ID to the client





@app.route('/generate_response_task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    task = celery.AsyncResult(task_id)

    print("Task state: ", task.state)

    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state == 'SUCCESS':
        tokens_used = task.result[1]

        charge_for_message = PRICE_PER_1_TOKEN * tokens_used
        print(f"Charge for message: {charge_for_message} USD")

        unique_azz_id = session.get("unique_azz_id")

        result_charge_for_message = collection.update_one({"unique_azz_id": unique_azz_id}, {"$inc": {"balance": -charge_for_message, "assistant_fund": charge_for_message}})
        response = {
            'state': task.state,
            'result': replace_markdown_images(task.result[0]),  # Task result when completed
            'status': 'Task completed!'
        }
    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'status': str(task.info)  # Exception message if failed
        }
    else:
        response = {
            'state': task.state,
            'status': task.state  # Other states like 'RETRY'
        }

    return jsonify(response)

def replace_markdown_images(text):
    # Regular expression pattern to find ![text](url)
    pattern = r'!\[(.*?)\]\((.*?)\)'
    
    # Function to replace the matched pattern with the desired <img> tag
    def replace_match(match):
        alt_text = match.group(1)
        src_url = match.group(2)
        return f'<img src="{src_url}" alt="Image of {alt_text}" width="170" height="auto">'
    
    # Use re.sub to replace all occurrences of the pattern
    return re.sub(pattern, replace_match, text)


### Celery part END ### 



@app.route('/trigger_generate_response_VOICE_ONLY/<unique_azz_id>', methods=['POST'])
def trigger_generate_response_VOICE_ONLY(unique_azz_id):
    data = request.form
    print(data)
    user_message = data.get('message', '')
    thread_id = data.get('thread_id')
    assistant_id = data.get('assistant_id')
    language = data.get("language", "en-US")[:2]

    # Retrieve other parameters
    restaurant_instance = collection.find_one({"unique_azz_id": unique_azz_id})
    payment_on = restaurant_instance.get("paymentGatewayTurnedOn")
    discovery_mode = restaurant_instance.get('discovery_mode')
    menu_file_id = restaurant_instance.get("menu_file_id")
    res_currency = restaurant_instance.get("res_currency")
    html_menu_tuples = restaurant_instance.get('html_menu_tuples')
    
    # Default image URL if no link is available
    default_image_url = "https://png.pngtree.com/png-vector/20221125/ourmid/pngtree-no-image-available-icon-flatvector-illustration-pic-design-profile-vector-png-image_40966566.jpg"

    # Iterate over each item in the 'html_menu_tuples' list
    for item in html_menu_tuples:
        # Step 1: Check if "Link to Image" is empty
        if not item.get('Link to Image'):
            # Step 2: If "Link to Image" is empty, check if "AI-Image" exists
            if item.get('AI-Image'):
                # Assign the AI image URL to "Link to Image"
                item['Link to Image'] = item['AI-Image']
                # Remove the 'AI-Image' field after assigning its value
                del item['AI-Image']
            else:
                # Step 3: If "AI-Image" does not exist, assign the default image URL
                item['Link to Image'] = default_image_url
    
    list_of_image_links = None  # Set or retrieve if necessary

    print("\n\n\n", html_menu_tuples, "\n\n\n")

    # Trigger the asynchronous task
    task = get_assistants_response_celery_VOICE_ONLY.apply_async(
        args=[
            user_message, language, thread_id, assistant_id, menu_file_id, 
            payment_on, html_menu_tuples, list_of_image_links, unique_azz_id, res_currency, discovery_mode
        ]
    )

    return jsonify({"task_id": task.id}), 202  # Return task ID to the client



@app.route('/generate_response_VOICE_ONLY_task_status/<task_id>', methods=['GET'])
def task_status_VOICE_ONLY(task_id):
    task = celery.AsyncResult(task_id)

    print("Task state: ", task.state)

    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state == 'SUCCESS':
        tokens_used = task.result[1]

        charge_for_message = PRICE_PER_1_TOKEN * tokens_used
        print(f"Charge for message: {charge_for_message} USD")

        unique_azz_id = session.get("unique_azz_id")

        result_charge_for_message = collection.update_one({"unique_azz_id": unique_azz_id}, {"$inc": {"balance": -charge_for_message, "assistant_fund": charge_for_message}})
        response = {
            'state': task.state,
            'result': replace_markdown_images(task.result[0]),  # Task result when completed
            'status': 'Task completed!'
        }
    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'status': str(task.info)  # Exception message if failed
        }
    else:
        response = {
            'state': task.state,
            'status': task.state  # Other states like 'RETRY'
        }

    return jsonify(response)

def replace_markdown_images(text):
    # Regular expression pattern to find ![text](url)
    pattern = r'!\[(.*?)\]\((.*?)\)'
    
    # Function to replace the matched pattern with the desired <img> tag
    def replace_match(match):
        alt_text = match.group(1)
        src_url = match.group(2)
        return f'<img src="{src_url}" alt="Image of {alt_text}" width="170" height="auto">'
    
    # Use re.sub to replace all occurrences of the pattern
    return re.sub(pattern, replace_match, text)










@app.route('/generate_response/<unique_azz_id>', methods=['POST', 'GET'])
def generate_response(unique_azz_id):
    # Set the environment variable for Google Cloud credentials
    # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\Users\mmatr\AppData\Roaming\gcloud\application_default_credentials.json'
    

    restaurant_instance = collection.find_one({"unique_azz_id": unique_azz_id})
    payment_on = restaurant_instance.get("paymentGatewayTurnedOn")
    discovery_mode = restaurant_instance.get('discovery_mode')
    
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

    html_menu_tuples = restaurant_instance.get('html_menu_tuples')
    #soup = BeautifulSoup(html_menu, 'html.parser')
    #rows = soup.find_all('tr')[1:]  # Skip the header row

    """
    list_of_all_items = []
    list_of_all_items_names_images = []
    list_of_image_links = []
    for row in rows:
        columns = row.find_all('td')
        item = columns[0].text
        ingredients = columns[1].text
        price = columns[2].text
        if len(columns) > 3:
            if columns[3]:
                image_link = columns[3].text
                list_of_image_links.append(image_link)
                items_image = f'<img src="{image_link}" alt="Image of {item}" width="170" height="auto">'
                tuple_we_deserved = (f"Item Name:{item}", f"Item Ingredients:{ingredients}", f"Items Price: {price} EUR", f"Image for {item}: {items_image}")
        else:
            tuple_we_deserved = (f"Item Name:{item}", f"Item Ingredients:{ingredients}", f"Items Price: {price} EUR")
        #list_of_all_items.append(tuple_we_deserved)
        list_of_all_items.append(tuple_we_deserved)
    """
    # print("List of image links formed: ", list_of_image_links)
    
    #print(f"\n\nList of all items formed: {list_of_all_items}\n\n")  # Debugging line

    print("Thats what we sent to retrieve the gpts response, ", user_input)
    response_llm, tokens_used = get_assistants_response(user_input, language, thread_id, assistant_id, menu_file_id, CLIENT_OPENAI, payment_on, list_of_all_items=html_menu_tuples, list_of_image_links=None, unique_azz_id=unique_azz_id, res_currency=res_currency, discovery_mode=discovery_mode)

    response_llm = replace_markdown_images(response_llm)
    
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


def replace_markdown_images(text):
    # Regular expression pattern to find ![text](url)
    pattern = r'!\[(.*?)\]\((.*?)\)'
    
    # Function to replace the matched pattern with the desired <img> tag
    def replace_match(match):
        alt_text = match.group(1)
        src_url = match.group(2)
        return f'<img src="{src_url}" alt="Image of {alt_text}" width="170" height="auto">'
    
    # Use re.sub to replace all occurrences of the pattern
    return re.sub(pattern, replace_match, text)




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

# Endpoint to receive the POST request
@app.route('/set_session_ordertype', methods=['POST'])
def set_session_ordertype():
    # Get the data from the request
    data = request.get_json()

    session["orderType"] = data.get('orderType')
    session["text_address"] = data.get('text_address')
    session["user_longitude"] = data.get('user_longitude')
    session["user_latitude"] = data.get('user_latitude')

    return jsonify({"success": True})

@app.route('/takeaway_delivery/<unique_azz_id>/', defaults={'order_id': None})
@app.route("/takeaway_delivery/<unique_azz_id>/<order_id>")
def takeaway_delivery_template(unique_azz_id, order_id):
    restaurant = collection.find_one({"unique_azz_id": unique_azz_id})

    payment_on = restaurant.get("paymentGatewayTurnedOn")

    if not order_id:
        order_id = cache.get("order_id")
    
    if payment_on:
        next_link = f"/payment_buffer/{unique_azz_id}/{order_id}"
    else:
        next_link = f"/no-payment-order-placed/{unique_azz_id}/{order_id}"

    print(f"\n\n\nNext link: {next_link}\n\n\n")
    
    location_coord = restaurant.get("location_coord")

    location_coord = json.loads(location_coord)

    restaurant_latitude = location_coord["lat"]
    restaurant_longtitude = location_coord["lng"]

    restaurant_delivery_radius = restaurant.get("radius_delivery_value")
    delivery_offered = restaurant.get("delivery_offered")
    
    # Render the template that asks the user for delivery or takeaway options
    restaurant_address = restaurant.get("location_name")
    return render_template('/payment_routes/takeaway_delivery_ask.html', 
                           title="Choose Place",
                           restaurant_latitude=restaurant_latitude,
                           restaurant_longtitude=restaurant_longtitude,
                           restaurant_delivery_radius=restaurant_delivery_radius,
                           GOOGLE_MAPS_API_KEY = GOOGLE_MAPS_API_KEY, 
                           restaurant_address=restaurant_address,
                           delivery_offered=delivery_offered,
                           next_link=next_link,
                           order_id=order_id)

@app.route('/submit_address', methods=['POST'])
def submit_address():
    # Retrieve the address from the request
    delivery_address = request.form.get('delivery_address')

    if delivery_address:
        # For now, just return a confirmation or process the address as needed
        # You can add additional logic here (e.g., save to a database, etc.)
        return jsonify({"status": "success", "message": f"Delivery address received: {delivery_address}"})
    else:
        return jsonify({"status": "error", "message": "No address provided"}), 400


@app.route('/no-payment-order-placed/<unique_azz_id>/', methods=["POST", "GET"], defaults={'order_id': None})
@app.route("/no-payment-order-placed/<unique_azz_id>/<order_id>", methods=["POST", "GET"])
def no_payment_order_placed(unique_azz_id, order_id):
    suggest_web3_bonus = cache.get("suggest_web3_bonus")

    # if not session.get('access_granted_no_payment_order'):
        # abort(403)  # Forbidden
    # Find the instance in MongoDB
    current_restaurant_instance = collection.find_one({"unique_azz_id": unique_azz_id})
    print(f"Restaurant with {unique_azz_id} found: {current_restaurant_instance}")

    order_from_db = db_order_dashboard[unique_azz_id].find_one({"orderID": order_id})

    orderType = session.get('orderType')
    text_address = session.get('text_address')
    user_longitude = session.get('user_longitude')
    user_latitude = session.get('user_latitude')

    if not order_from_db:
        order_id = cache.get("order_id")
        total_price_EUR = cache.get("total_price_EUR")
        total_price_NATIVE = cache.get("total_price_NATIVE")
        items_ordered = cache.get("items_ordered")
    else:
        total_price_EUR = order_from_db.get("total_paid_EUR")
        total_price_NATIVE = order_from_db.get("total_paid_NATIVE")
        items_ordered = order_from_db.get("items")
    
    
    res_currency = current_restaurant_instance.get("res_currency")
    restaurant_name = current_restaurant_instance.get("name")
    NEW_ORDER_MESSAGE = f"New order for {restaurant_name.replace('_', ' ')} has been published! 🚀🚀🚀"
    
    # Convert the timestamp to a datetime object
    current_utc_timestamp = time.time()
    utc_datetime = datetime.utcfromtimestamp(current_utc_timestamp)

    # Format the datetime object to a human-readable string
    human_readable_time_format = utc_datetime.strftime('%Y-%m-%d %H:%M')



    if orderType == "delivery":
        order_to_pass = {"items":[{'name':item['name'], 'quantity':item['quantity']} for item in items_ordered], 
                            "orderID":order_id,
                            "timestamp": human_readable_time_format,
                            "total_paid": total_price_NATIVE,
                            "total_paid_EUR": total_price_EUR,
                            "mom_ai_restaurant_assistant_fee": 0,
                            "paypal_fee": 0,
                            "paid":"NOT PAID",
                            "order_type": orderType,
                            "link_of_user_address": f"https://www.google.com/maps?q={user_latitude},{user_longitude}",
                            "text_address": text_address,
                            "published":True}
    else:
        order_to_pass = {"items":[{'name':item['name'], 'quantity':item['quantity']} for item in items_ordered], 
                            "orderID":order_id,
                            "timestamp": human_readable_time_format,
                            "total_paid": total_price_NATIVE,
                            "total_paid_EUR": total_price_EUR,
                            "mom_ai_restaurant_assistant_fee": 0,
                            "paypal_fee": 0,
                            "paid":"NOT PAID",
                            "order_type": orderType,
                            "published":True}
    
    
    db_order_dashboard[unique_azz_id].update_one(
    {"orderID": order_to_pass["orderID"]},
    {"$set": order_to_pass},
    upsert=True
    )
    # print("\n\nInserted the order in db_order_dashboard with if ", unique_azz_id, "\n\n")
    
    items = items_ordered

    ordered_items_names = [item["name"] for item in items]

    image_urls = []

    restaurant_menu = current_restaurant_instance.get("html_menu_tuples")

    for item_ordered_name in ordered_items_names:
        for item_menu in restaurant_menu:
            if sorted(item_menu["Item Name"].lower().split()) == sorted(item_ordered_name.lower().split()):
                print(sorted(item_menu["Item Name"].lower().split()))
                print(sorted(item_ordered_name.lower().split()))
                image_urls.append(item_menu.get("Link to Image"))
                found_match = True
                break
        if not found_match:
            image_urls.append(None)


    for index, image_url in enumerate(image_urls):
        items[index]['image_url'] = image_url
    
    all_ids_chats = current_restaurant_instance.get("notif_destin", [])

    for chat_id in all_ids_chats:
        send_telegram_notification(chat_id)


    if suggest_web3_bonus:
        cache.delete("suggest_web3_bonus")

    # suggest_web3_bonus = True
    
    # Get current UTC time and format it as dd.mm hh:mm
    # timestamp_utc = datetime.utcnow().strftime('%d.%m.%Y %H:%M')
    return render_template("payment_routes/no_payment_order_finish.html", 
                           title="Ready Order", 
                           res_unique_azz_id=unique_azz_id, 
                           order_id=order_id,
                           total_price_EUR=total_price_EUR,
                           total_price_NATIVE=total_price_NATIVE,
                           res_currency=res_currency, 
                           restaurant_name=restaurant_name.replace('_', ' '), 
                           items=items_ordered,
                           suggest_web3_bonus=suggest_web3_bonus,
                           unique_azz_id=unique_azz_id)




@app.route('/success_payment_backend/<unique_azz_id>', methods=["POST", "GET"])
def success_payment_backend(unique_azz_id):
    suggest_web3_bonus = request.args.get("suggest_web3_bonus")
    
    if suggest_web3_bonus:
        cache.set("suggest_web3_bonus", True)
    else:
        cache.set("suggest_web3_bonus", False)

    orderType = session.get('orderType')
    text_address = session.get('text_address')
    user_longitude = session.get('user_longitude')
    user_latitude = session.get('user_latitude')
    
    print("Setup suggest web3 hours in session to ", cache.get("suggest_web3_bonus"))
    
    if not cache.get('access_granted_payment_result'):
        abort(403)  # Forbidden

    session.pop('access_granted_payment_buffer', None)
    
    items = cache.get('items_ordered')
    total_paid_EUR = cache.get("total_to_pay_EUR")
    total_paid_native = cache.get("total_to_pay_native")
    order_id = cache.get("order_id")

    sum_of_order = cache.get('sum_of_order')

    #total_received = float(round(float(round(float(total_paid),2))*0.99, 2)) # 1 percent retained for prOOOOOOfit
    
    MOM_AI_FEE = float(round(float(round(float(sum_of_order),2))*0.01, 2))+0.10 # 1 percent retained for prOOOOOOfit
    PAYPAL_FEE = 0.35+float(round(float(round(float(sum_of_order),2))*0.0349, 2))

    print(f"MOM AI fee in the order: {MOM_AI_FEE}\n\n")
    print(f"PAYPAL fee in the order: {PAYPAL_FEE}\n\n")

    total_received = float(total_paid_EUR) - float(round(MOM_AI_FEE, 2)) - float(round(PAYPAL_FEE, 2))

    print(f"That's how much customer paid: {total_paid_EUR}")
    print(f"That's how much restaurant received: {total_received}")

    # Find the instance in MongoDB
    current_restaurant_instance = collection.find_one({"unique_azz_id": unique_azz_id})
    print(f"Restaurant with {unique_azz_id} found: {current_restaurant_instance}")

    # Get current UTC time and format it as dd.mm hh:mm
    timestamp_utc = datetime.utcnow().strftime('%d.%m.%Y %H:%M')

    # Create Item instances for each item in the request
    #items = [Item(name=item['name'], quantity=item['quantity']) for item in items_data]
    
    assistant_used = cache.get("unique_azz_id")
    
    if orderType == "delivery":
        order_to_pass = {"items":[{'name':item['name'], 'quantity':item['quantity']} for item in items], 
                            "orderID":order_id,
                            "timestamp": timestamp_utc,
                            "total_paid": total_paid_native,
                            "total_paid_EUR": total_paid_EUR,
                            "mom_ai_restaurant_assistant_fee": float(round(MOM_AI_FEE, 2)),
                            "paypal_fee": float(round(PAYPAL_FEE, 2)),
                            "paid":"PAID",
                            "order_type": orderType,
                            "link_of_user_address": f"https://www.google.com/maps?q={user_latitude},{user_longitude}",
                            "text_address": text_address,
                            "published":True}
    else:
        order_to_pass = {"items":[{'name':item['name'], 'quantity':item['quantity']} for item in items], 
                            "orderID":order_id,
                            "timestamp": timestamp_utc,
                            "total_paid": total_paid_native,
                            "total_paid_EUR": total_paid_EUR,
                            "mom_ai_restaurant_assistant_fee": float(round(MOM_AI_FEE, 2)),
                            "paypal_fee": float(round(PAYPAL_FEE, 2)),
                            "paid":"PAID",
                            "order_type": orderType,
                            "published":True}
    
    order_dashboard_id = assistant_used

    db_order_dashboard[order_dashboard_id].insert_one(order_to_pass)


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
    print(f"Total paid: {total_paid_EUR} on success payment route")


    flash("Your Order was Successfully Placed!", "success")

    # This route can be used for further processing if needed
    return redirect(url_for('success_payment_display', unique_azz_id=unique_azz_id, id=order_id))



@app.route('/success_payment/<unique_azz_id>/<id>', methods=["GET", "POST"])
def success_payment_display(unique_azz_id, id):
    suggest_web3_bonus = cache.get("suggest_web3_bonus") or False

    print("Suggest web3 bonus, ", suggest_web3_bonus)
    
    if not id:
        abort(403)
    current_restaurant_instance = collection.find_one({"unique_azz_id": unique_azz_id})
    restaurant_name = current_restaurant_instance.get("name")
    result = db_items_cache[unique_azz_id].delete_one({"id":id})
    restaurant_menu = current_restaurant_instance.get("html_menu_tuples")
    res_currency = current_restaurant_instance.get("res_currency")
    
    order = db_order_dashboard[unique_azz_id].find_one({"orderID": id})

    items = order.get("items")

    ordered_items_names = [item["name"] for item in items]

    image_urls = []

    for item_ordered_name in ordered_items_names:
        for item_menu in restaurant_menu:
            if sorted(item_menu["Item Name"].lower().split()) == sorted(item_ordered_name.lower().split()):
                print(sorted(item_menu["Item Name"].lower().split()))
                print(sorted(item_ordered_name.lower().split()))
                image_urls.append(item_menu.get("Link to Image"))
                found_match = True
                break
        if not found_match:
            image_urls.append(None)


    for index, image_url in enumerate(image_urls):
        items[index]['image_url'] = image_url

    order_from_db = db_order_dashboard[unique_azz_id].find_one({"orderID": id})

    total_paid_EUR = order_from_db.get('total_paid_EUR')
    total_paid_NATIVE = order_from_db.get('total_paid')

    # Check if the delete was successful
    if result.deleted_count > 0:
        print("Document deleted.")
    else:
        print("No document matches the query. Nothing was deleted.")

    if cache.get("suggest_web3_bonus"):
        cache.delete("suggest_web3_bonus")

    return render_template('payment_routes/success_payment.html', title="Payment Successful", restaurant_name=restaurant_name, 
                           res_unique_azz_id=unique_azz_id, 
                           order_id=id, 
                           suggest_web3_bonus=suggest_web3_bonus, 
                           items=items,
                           total_paid_EUR=total_paid_EUR,
                           unique_azz_id=unique_azz_id,
                           total_price_NATIVE=total_paid_NATIVE,
                           res_currency=res_currency)
    

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
    print("We are on the request withdrawal post endpoint")
    res_email = session.get('restaurant_email')
    res_name = session.get('restaurant_name')
    withdraw_amount = round(session.get("current_balance")-10, 2)

    print("Withdraw amount: ", withdraw_amount)

    send_confirmation_email_request_withdrawal(mail, res_email, res_name, withdraw_amount, withdrawal_description, FROM_EMAIL)
    current_restaurant_instance = collection.find_one({"email": res_email})
    
    if current_restaurant_instance.get("await_withdrawal"):
        print("Chose IF")
        result_withdraw_request = collection.update_one({"email":res_email}, {"$set": {"balance": 10}, "$inc": {"await_withdrawal": withdraw_amount}})
    else:
        print("Chose ELSE")
        result_withdraw_request = collection.update_one({"email":res_email}, {"$set": {"balance": 10, "await_withdrawal": withdraw_amount}})
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
            'paid':order.get('paid'),
            'order_type': order.get('order_type')

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

@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    email = request.json.get('email')
    restaurant = collection.find_one({"email": email})
    unique_azz_id = restaurant.get('unique_azz_id')
    password = restaurant.get('password')

    reset_password_code = restaurant.get('reset_password_code')

    if restaurant:
        send_email_raw(mail, email, f"<p style='font-size: 16px; line-height: 1.5;'>Your recovery link is <a href='https://mom-ai-restaurant.pro/reset_password?unique_azz_id={unique_azz_id}&reset_password_code={reset_password_code}'>here</a></p>", "Password Recovery", FROM_EMAIL)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@app.route('/reset_password', methods=['POST', 'GET'])
def reset_password():
    unique_azz_id = request.args.get('unique_azz_id')
    reset_password_code = request.args.get('reset_password_code')
    
    restaurant = collection.find_one({"unique_azz_id": unique_azz_id})
    real_reset_password_code = restaurant.get('reset_password_code')
    
    if not unique_azz_id or not reset_password_code or real_reset_password_code != reset_password_code:
        abort(404)

    form = ResetPasswordForm()
    if form.validate_on_submit():
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data
        if new_password == confirm_password:
            print("Passwords match")
            # Update the password in the database
            collection.update_one({"unique_azz_id": unique_azz_id}, {"$set": {"password": hash_password(new_password), "reset_password_code": generate_random_string(10)}})
            flash("Password has been changed successfully! Please, log in again.", "success")
            return redirect(url_for('login'))
        else:
            print("Passwords do not match")
            flash("Passwords do not match", "danger")
    return render_template('start/reset_password.html', form=form, title="Reset Password")
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

    html_menu = restaurant.get("html_menu_tuples")

    restaurant_reviews = db_rest_reviews[unique_azz_id]
    
    reviews = restaurant_reviews.find()

    reviews = list(reviews)

    html_menu_tuples = restaurant.get("html_menu_tuples")

    menu_images = restaurant.get("menu_images", [])

    print(menu_images)

    print("Menu tuples we passed: ", html_menu_tuples)

    there_are_reviews = True if len(reviews)>=1 else False
    
    working_schedule = restaurant.get("working_schedule")
    
    start_work = [day['start'] if not day['dayOff'] else 777 for day in working_schedule]
    end_work = [day['end'] if not day['dayOff'] else 777 for day in working_schedule]

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

    start_working_hours = [convert_hours_to_time(hour) for hour in start_work]
    end_working_hours = [convert_hours_to_time(hour) for hour in end_work]

    print(start_work)
    print(end_work)
    
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
                           html_menu=html_menu,
                           reviews=reviews,
                           there_are_reviews=there_are_reviews,
                           html_menu_tuples=html_menu_tuples,
                           menu_images=menu_images)


@app.route('/google-callback', methods=['POST'])
def google_callback():
    # Get the token from the request
    
    token = request.json.get('token')
    type_ = request.args.get("type")

    # print("Token: ", token)

    try:
        print("Entered 'try'")
        # Verify the token using Google's API
        id_info = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_OAUTH_CLIENT_ID)

        # If the token is valid, id_info will contain user data
        user_data = {
            "user_id": id_info.get("sub"),
            "email": id_info.get("email"),
            "name": id_info.get("name"),
            "picture": id_info.get("picture"),
        }

        restaurant = collection.find_one({"email": user_data["email"]})
 
        send_to_dashboard = False

        if restaurant:
            session["res_email"] = restaurant.get("email")
            send_to_dashboard = True

        print(user_data)

        session["res_email"] = user_data["email"]
        session['access_granted_assistant_demo_chat'] = True

        # Here you can process user data (e.g., log them in, create an account, etc.)
        return jsonify({
            "success": True,
            "user_data": user_data,
            "send_to_dashboard": send_to_dashboard
        }), 200

    except ValueError as e:
        flash(e)

        # Token is invalid, return an error response
        return jsonify({
            "success": False,
            "message": "Invalid token",
            "type": type_
        }), 400


@app.route('/search_instance/<unique_azz_id>', methods=['POST', 'GET'])
def search_instance(unique_azz_id):
    # unique_azz_id = request.json.get('unique_azz_id')
    
    if request.method == 'OPTIONS':
        # Handling OPTIONS request
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
    
    if not unique_azz_id:
        return jsonify({"success": False, "message": "No unique_azz_id provided"}), 400
    
    try:
        restaurant = collection.find_one({"unique_azz_id": unique_azz_id})

        name = restaurant.get("name")
        res_currency = restaurant.get("res_currency")
        list_of_items = restaurant.get("html_menu_tuples")
        menu_string = ""
        for item in list_of_items:
            menu_string += f"{item['Item Name']} - {item['Item Description']} - {item['Item Price (EUR)']} {res_currency}\n"
        
        assistant_turned_on = restaurant.get("assistant_turned_on")
        is_open = restaurant.get("isOpen")
        address = restaurant.get("location_name")
        delivery_offered = restaurant.get("delivery_offered")
        discovery_mode_is_on = restaurant.get("discovery_mode")

        object_to_send = {"unique_azz_id": unique_azz_id,
                          "name": name, 
                          "menu_string": menu_string,
                          "assistant_turned_on": assistant_turned_on, 
                          "is_open": is_open,
                          "address": address,
                          "delivery_available": delivery_offered,
                          "discovery_mode_is_on": discovery_mode_is_on}

        if restaurant:
            return jsonify({"success": True, "restaurant": object_to_send}), 200
        else:
            return jsonify({"success": False, "message": "No restaurant found with the provided unique_azz_id"}), 404
    
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500


@app.route('/accept-order-details-voice', methods=['POST', 'GET', 'OPTIONS'])
def accept_order_details_voice():
    
    if request.method == 'OPTIONS':
        print("Handling OPTIONS request")
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    try:
        print("Entering try block")
        # Get the JSON payload from the request
        payload = request.json

        print("Received payload:", payload)
        
        if not payload:
            print("Error: No JSON payload received")
            return jsonify({"error": "No JSON payload received"}), 400
        
        order_id = payload.get('id')
        print("Order ID:", order_id)
        
        unique_azz_id = payload.get('restaurant_id')
        print("Restaurant ID:", unique_azz_id)
        
        restaurant = collection.find_one({"unique_azz_id": unique_azz_id})
        print("Restaurant data:", restaurant)
        
        res_currency = restaurant.get("res_currency")
        print("Restaurant currency:", res_currency)
        
        payment_on = restaurant.get("paymentGatewayTurnedOn")
        print("Payment gateway turned on:", payment_on)
        
        items_ordered = payload.get('items_ordered')
        print("Items ordered:", items_ordered)
        
        total_price_native = payload.get('totalAmount')
        print("Total price (native):", total_price_native)

        current_utc_timestamp = time.time()
        print("Current UTC timestamp:", current_utc_timestamp)

        # Convert the timestamp to a datetime object
        utc_datetime = datetime.utcfromtimestamp(current_utc_timestamp)
        print("UTC datetime:", utc_datetime)

        # Format the datetime object to a human-readable string
        human_readable_time_format = utc_datetime.strftime('%Y-%m-%d %H:%M')
        print("Human-readable time format:", human_readable_time_format)

        if res_currency != 'EUR':
            rate = c.convert(1, res_currency, 'EUR')
        else:
            rate = 1
        print("Conversion rate to EUR:", rate)

        print("Items ordered set in cache")

        if payment_on:
            print("Payment gateway is on")
            # print("Currency and rate set in cache")
            
            db_items_cache[unique_azz_id].insert_one({"data": items_ordered, "id": order_id, "timestamp": current_utc_timestamp})
            print("Order inserted into db_items_cache")
            next_link = f"/payment_buffer/{unique_azz_id}/{order_id}"
            print("Next link (payment on):", next_link)
        else:

            total_price_EUR = total_price_native * rate

            print("\n\n\nTotal price in EUR:", total_price_EUR, "\n\n\n")
            
            order_to_pass = {
                "items": [{'name': item['name'], 'quantity': item['quantity']} for item in items_ordered],
                "orderID": order_id,
                "timestamp": human_readable_time_format,
                "total_paid": total_price_native,
                "total_paid_EUR": total_price_EUR,
                "mom_ai_restaurant_assistant_fee": 0,
                "paypal_fee": 0,
                "paid": "NOT PAID",
                "published": True
            }
            print("Order to pass:", order_to_pass)
        
            db_order_dashboard[unique_azz_id].insert_one(order_to_pass)
            print("Order inserted into db_order_dashboard")
            
            next_link = f"/no-payment-order-placed/{unique_azz_id}"
            print("Next link (payment off):", next_link)
        
        print("Next take delivery link set in cache:", next_link)

        print("Preparing response")
        return jsonify({
            "message": "Order details received successfully",
            "order_details": payload,
            "next_link": next_link
        }), 200

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500


    
if __name__ == '__main__':
    socketio.run(app, debug=True, host='localhost', port=5000, use_reloader=True)




    
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