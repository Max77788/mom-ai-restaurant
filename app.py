from flask import Flask, abort, make_response, jsonify, request, render_template, session, redirect, url_for, flash, render_template_string, Response, send_file
from werkzeug.utils import secure_filename
import os
import gridfs
from bs4 import BeautifulSoup
#from pyrogram import filters
#from utils.telegram import app_tg
from utils.forms import RestaurantForm, UpdateMenuForm, ConfirmationForm, LoginForm, RestaurantFormUpdate 
from utils.functions import InvalidMenuFormatError, upload_new_menu, convert_xlsx_to_txt_and_menu_html, create_assistant, insert_document, get_assistants_response, send_confirmation_email, generate_confirmation_code, check_credentials, send_telegram_notification, send_confirmation_email_request_withdrawal, send_waitlist_email, send_email 
from pymongo import MongoClient
from flask_mail import Mail, Message
from utils.web3_functionality import create_web3_wallet, completion_on_binance_web3_wallet_withdraw
import base64
#from utils.hyperwallet import create_user, create_bank_account, make_payment
import ast
from utils.pp_payment import createPayment, executePayment, get_subscription_status, createOrder, captureOrder
#from utils.withdraw.pp_payout import send_payout_pp
from datetime import datetime
from openai import OpenAI, AzureOpenAI
from bson import ObjectId  # Import ObjectId from bson
import io
#from tools.stellar_payments.list_payments import list_received_payments
#from tools.stellar_payments.create_account import create_stellar_account
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY")
app.config['UPLOAD_FOLDER'] = 'uploads'

CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID") if os.environ.get("PAYPAL_SANDBOX") == "True" else os.environ.get("PAYPAL_LIVE_CLIENT_ID")
SECRET_KEY = os.environ.get("PAYPAL_SECRET_KEY") if os.environ.get("PAYPAL_SANDBOX") == "True" else os.environ.get("PAYPAL_LIVE_SECRET_KEY")

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
db = client_db['MOM_AI_Restaurants']

# Specify the collection name
collection = db[os.environ.get("DB_VERSION")]

db_order_dashboard = client_db["Dashboard_Orders"]

CLIENT_OPENAI = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
"""
CLIENT_OPENAI = AzureOpenAI(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),  
    api_version="2024-02-15-preview",
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
)
"""


fs = gridfs.GridFS(db)

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


@app.errorhandler(403)
def forbidden(error):
    return make_response(jsonify({'error': 'Forbidden', 'message': error.description}), 403)


# Middleware to modify headers
@app.after_request
def add_header(response):
    response.headers['X-Frame-Options'] = 'ALLOWALL'  # Allow all domains to embed
    return response

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
    
"""


#################### Registration/Login Part Start ####################

@app.route('/', methods=['GET', 'POST'])
def landing_page():
    #session.clear()  # Clear session for clean state testing
    #print("Session cleared")

    #if session.get("res_email"):
        #return redirect(url_for("notify_waitlist"))

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
        print(f"Restaurant password: {password}")

        currency = form.currency.data
        print(f"Currency of the restaurant: {currency}")

        session["currency"] = currency

        # Save the image to GridFS
        image = form.image.data
        print(f'Image Received:{image}')
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

            menu_save_path = os.path.join(app.config['UPLOAD_FOLDER'], "menu_file.txt")
            
            menu_txt_path, html_menu = convert_xlsx_to_txt_and_menu_html(menu_xlsx_path, menu_save_path, currency)
            
            if not isinstance(menu_txt_path, str):
               print("Entered Invalid Menu Error.")
               flash(str(menu_txt_path))
               return redirect("/")
            print(f"Generated menu txt file: {menu_txt_path}")

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
            generated_confirmation_code = generate_confirmation_code()  # You need to implement this

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
        generated_confirmation_code = generate_confirmation_code()  # You need to implement this

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
    
    return render_template('start/landing.html', form=form, title="Restaurant Assistant")

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
    return render_template('start/login.html', form=form, title="Login")

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Clear the session
    flash('You logged out successfully')  # Add a flash message
    return redirect(url_for('login'))  # Redirect to dashboard

#################### Registration/Login Part End ####################



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
                return redirect(url_for('confirm_email'))
        else:
            flash('Invalid confirmation code. Please try again.', 'error')

    return render_template('email_confirm/enter_code.html', form=form, res_email=res_email, title="Enter Confirmation Code")


@app.route('/confirm_email')
def confirm_email():
    # Check if the session variable is set
    if not session.get('access_granted_email_confirm_page'):
        abort(403)  # Forbidden
    
    # Clear the session variable after access
    session.pop('access_granted_email_confirm_page', None)
    
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
        messages.append({'sender': 'assistant', 'content': "I do not know yet what to say as I am not an AI yet. But in 10 seconds you will be redirected and magic will happen."})
    
    session['messages'] = messages
    print(messages)
    
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

    verified_res_email = session.get("verified_res_email", "email_placeholder")

    restaurant_name = session.get("restaurant_name")
    
    website_url = session.get("res_website_url", "Restaurant URL placeholder")

    menu_file_id = session.get("menu_file_id")
    menu_vector_id = session.get("menu_vector_id")

    currency = session.get("currency")
    html_menu = session.get("html_menu")

    file_id = session.get("logo_id", "666af654dee400a1d635eb08")

    insert_document(collection, res_name, verified_res_email, res_password, website_url, assistant_id, menu_file_id, menu_vector_id, currency, html_menu, wallet_public_key_address="None", wallet_private_key="None", logo_id=file_id)
    send_confirmation_email(mail, verified_res_email, restaurant_name, FROM_EMAIL)
    #send_waitlist_email(mail, verified_res_email, restaurant_name, FROM_EMAIL)

    # Clear the session variable after access
    session.pop('access_granted_assistant_demo_chat', None)
      
    session["access_granted_waitlist_page"] = True
    
    return render_template("start/demo.html", title="Demo Chat", messages=messages, restaurant_name=restaurant_name)

#################### Demo Chat Part End ####################





#################### Dashboard Part Main App ####################
'''
@app.route('/market_dashboard')
def market_dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 12  # 2 columns * 6 rows
    restaurants, total = get_restaurants(page, per_page)  # Function to fetch paginated restaurant data
    return render_template('marketing_dashboard/market_dashboard.html', restaurants=restaurants, page=page, per_page=per_page, total=total, title="AI Restaurants Market")

def get_restaurants(page, per_page):
    skip = (page - 1) * per_page
    cursor = collection.find().skip(skip).limit(per_page)
    total = collection.count_documents({})
    restaurants = list(cursor)
    return restaurants, total
'''

@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard_display():
    print("Jumped on display dashboard link")
    res_email = session.get("res_email")
    res_password = session.get("password")

    # Find the instance in MongoDB
    restaurant_instance = collection.find_one({"email": res_email, "password": res_password})

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

        print(f"Assistant ID added in session: {assistant_id}")
        print(f"Restaurant name added in session: {restaurant_name}")
        
        logo_url = url_for('serve_image', file_id=logo_id)

    else:
        # Handle the case when the instance is not found
        flash("Restaurant not found.")
        return redirect(url_for("landing_page"))
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
                           restaurant=restaurant_instance)

###################################### Dashboard Buttons ######################################

@app.route('/payments', methods=['POST', 'GET'])
def payments_display():
    
    #restaurant_name = session.get("restaurant_name")
    #restaurant_email = session.get("restaurant_email")
    unique_azz_id = session.get("unique_azz_id")

    restaurant = collection.find_one({"unique_azz_id":unique_azz_id})
    print(restaurant)
    
    order_dashboard_id = unique_azz_id

    orders = db_order_dashboard[order_dashboard_id].find()

    payments = [{"timestamp":order.get("timestamp"), "total_paid":round(order.get("total_paid"),2)} for order in orders]

    return render_template("dashboard/payments_history.html", payments=payments, restaurant=restaurant)

@app.route('/profile')
def show_restaurant_profile():
    # Retrieve restaurant profile by unique_azz_id
    unique_azz_id = session.get("unique_azz_id")
    restaurant = collection.find_one({'unique_azz_id': unique_azz_id})
    restaurant_balance = round(restaurant.get("balance"), 2)
    connected_chats_len = len(restaurant.get("notif_destin", []))
    if restaurant:
        return render_template('dashboard/profile.html', restaurant=restaurant, restaurant_balance=restaurant_balance, connected_chats=connected_chats_len)
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
        elif attribute == 'notif_destin' and new_value:
            collection.update_one({'unique_azz_id': current_uni_azz_id},{'$push': {'notif_destin': new_value}})
            NEW_CHAT_MESSAGE = f"🔝You are the best\n\nYou have successfully setup notifications!\n\nMOM AI bot will notify you upon upcoming of new orders in this chat."
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
    return render_template("dashboard/menu_display.html", html_menu=html_menu, form=form)

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


@app.route('/payment_buffer/<unique_azz_id>', methods=['POST', 'GET'])
def payment_buffer(unique_azz_id):
    restaurant = collection.find_one({"unique_azz_id":unique_azz_id})
    items = session.get('items_ordered', [{"name":"Item1", "quantity":1, "amount":0.02}])
    print(f"Items on payment buffer: {items}")
    CURRENCY = session.get("res_currency", "USD")
    #checkout_link = session.get("paypal_link")
    total_to_pay = session.get("total", 0.07)
    total_to_pay = str(round(float(total_to_pay), 2))
    
    return render_template("payment_routes/payment_buffer.html", items=items, total_to_pay=total_to_pay, CLIENT_ID=CLIENT_ID, CURRENCY=CURRENCY, restaurant=restaurant, title="Payment Buffer")


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
   

@app.route("/execute_payment", methods=['POST','GET'])
def execute_payment():
    payment_id = request.args.get('paymentID')
    payer_id = request.args.get('payerID')
    print(f"Payment ID retrieved: {payment_id}")
    print(f"Payer ID retrieved: {payer_id}")
    
    if not payment_id or not payer_id:
        return jsonify({'error': 'Missing paymentID or payerID'}), 400

    exec_success = executePayment(payment_id, payer_id)

    if exec_success:
        return redirect(url_for("success_payment"))
    else:
        return redirect(url_for("cancel_payment"))

@app.route("/create_order", methods=['POST','GET'])
def create_order():
    order = createOrder()
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
    # Now you can use the orderID variable in your function
    print(f"Received orderID: {orderID}")
    captured_order = captureOrder(orderID).json()
    print(captured_order)

    if captured_order["status"] == "COMPLETED":
        return captured_order
    else:
        return jsonify({"error":True})


@app.route('/assistant_dash', methods=['POST', 'GET'])
def assistant_dashboard_route():
    sub_activated = session.get("subscription_activated")
    unique_azz_id = session.get("unique_azz_id")
    restaurant_name = session.get("restaurant_name")
    return render_template("dashboard/assistant_reroute.html", unique_azz_id=unique_azz_id, restaurant_name=restaurant_name, sub_activated=sub_activated) 

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
    thread = CLIENT_OPENAI.beta.threads.create(tool_resources={"file_search": 
                                                               {"vector_store_ids": [vector_store_id]}
                                                               })
    
    
    # Get current UTC time and format it as dd.mm hh:mm
    # timestamp_utc = datetime.utcnow().strftime('%d.%m.%Y %H:%M')
    # collection_threads.insert_one({"thread_id":thread.id, "restaurant_name":restaurant_name, "timestamp UTC":timestamp_utc})
    
    
    print(f"New thread created with ID: {thread.id}")  # Debugging line
    return jsonify({"thread_id": thread.id, "assistant_id": assistant_id})

@app.route('/assistant_order_chat/<unique_azz_id>')
def assistant_order_chat(unique_azz_id):
    # Retrieve the full assistant_id from the session
    
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

    session["unique_azz_id"] = unique_azz_id
    session["full_assistant_id"] = full_assistant_id
    session["menu_file_id"] = menu_file_id
    session["menu_vector_id"] = menu_vector_id
    session["res_currency"] = res_currency
    session["restaurant_name"] = restaurant_name
    # Use the restaurant_name from the URL and the full assistant_id from the session
    return render_template('dashboard/order_chat.html', restaurant_name=restaurant_name, assistant_id=full_assistant_id, unique_azz_id=unique_azz_id, restaurant_website_url=restaurant_website_url, title=f"{restaurant_name}'s Assistant", assistant_turned_on=assistant_turned_on, restaurant=res_instance, iframe=iframe)

# Generate response
@app.route('/generate_response/<unique_azz_id>', methods=['POST', 'GET'])
def generate_response(unique_azz_id):
    data = request.json
    thread_id = data.get('thread_id')
    assistant_id = data.get('assistant_id')
    user_input = data.get('message', '')
    restaurant_instance = collection.find_one({"unique_azz_id":unique_azz_id})
    menu_file_id = restaurant_instance.get("menu_file_id")
    res_currency = restaurant_instance.get("res_currency")
    print(f"Menu file ID on /generate_response: {menu_file_id}")

    print(f"User input: {user_input}")
    print(f"Thread ID: {thread_id}")
    print(f"Assistant ID: {assistant_id}")

    html_menu  = restaurant_instance.get('html_menu')

    soup = BeautifulSoup(html_menu, 'html.parser')
    rows = soup.find_all('tr')[1:]  # Skip the header row

    list_of_all_items = []
    for row in rows:
        columns = row.find_all('td')
        item = columns[0].text
        price = columns[2].text
        tuple_we_deserved = (item, f"{price} {res_currency}")
        list_of_all_items.append(tuple_we_deserved)

    print(f"\n\nList of all items formed: {list_of_all_items}\n\n") # debugging line

    response_llm, tokens_used = get_assistants_response(user_input, thread_id, assistant_id, res_currency, menu_file_id, CLIENT_OPENAI, list_of_all_items=list_of_all_items, unique_azz_id=unique_azz_id)
    PRICE_PER_1_TOKEN = 0.000007

    charge_for_message = PRICE_PER_1_TOKEN*tokens_used

    print(f"Charge for message: {charge_for_message} USD")

    unique_azz_id = session.get("unique_azz_id")

    result_charge_for_message = collection.update_one({"unique_azz_id":unique_azz_id}, {"$inc": {"balance": -charge_for_message, "assistant_fund": charge_for_message}})
    # Check if the update was successful
    if result_charge_for_message.matched_count > 0:
        print("Balances were successfully.")
    else:
        print("No matching document found.")


    
    print(f"LLM response: {response_llm}")

    if isinstance(response_llm, Response):
        # Handle the Response object differently
        # For example, you might want to convert it to a string or extract its data
        response_llm_data = response_llm.get_data(as_text=True)
        response_llm_dict = ast.literal_eval(response_llm_data)
        response_llm = response_llm_dict["response"]

    return jsonify({"response_llm":response_llm})

'''
@app.route('/setup_payments', methods=['POST', 'GET'])
def setup_payments():
    restaurant_name = session.get("restaurant_name", "restaurant")
    return render_template("setup_payments.html", title="Payment Setup", restaurant_name=restaurant_name)
'''



################## Payment routes/Order Posting ###################


@app.route('/success_payment', methods=["GET", "POST"])
def success_payment():
    
    restaurant_name = session.get("restaurant_name", "restaurant_placeholder")
    
    items = session.get('items_ordered', [{'name':'item1', 'quantity':1}, {'name':'item2', 'quantity':2}])
    total_paid = session.get('total', 9.95)
    total_received = float(round(float(round(float(total_paid),2))*0.99, 2)) # 1 percent retained for prOOOOOOfit

    print(f"That's how much customer paid: {total_paid}")
    print(f"That's how much restaurant received: {total_received}")
    
    res_email = session.get("res_email")

    # Find the instance in MongoDB
    current_restaurant_instance = collection.find_one({"email": res_email})
    print(f"Restaurant with {res_email} found: {current_restaurant_instance}")

    # Get current UTC time and format it as dd.mm hh:mm
    timestamp_utc = datetime.utcnow().strftime('%d.%m.%Y %H:%M')

    # Create Item instances for each item in the request
    #items = [Item(name=item['name'], quantity=item['quantity']) for item in items_data]
    
    assistant_used = session["unique_azz_id"]
    
    order_to_pass = {"items":[{'name':item['name'], 'quantity':item['quantity']} for item in items], 
                        "timestamp": timestamp_utc,
                        "total_paid": total_received,
                        "assistant_used": assistant_used,
                        "published":True}
    
    order_dashboard_id = assistant_used

    db_order_dashboard[order_dashboard_id].insert_one(order_to_pass)

    current_balance = current_restaurant_instance.get("balance")
    print(f"Current balance before updating: {current_balance}")

    result = collection.update_one({'email': res_email}, {"$inc": {"balance": total_received}})
    
    all_ids_for_acc = current_restaurant_instance.get('notif_destin')
    
    if all_ids_for_acc is not None:
        for chatId in all_ids_for_acc:
            send_telegram_notification(chat_id=chatId)
    
    # Check if the update was successful
    if result.matched_count > 0:
        print("Added funds for the order successfully.")
    else:
        print("No matching document found.")

    current_balance = current_restaurant_instance.get("balance")
    print(f"Current balance after updating: {current_balance}")

    print(f"Items: {items} on success payment route")
    print(f"Total paid: {total_received} on success payment route")

    res_unique_azz_id = session.get("unique_azz_id")

    flash("Your Order was Successfully Placed!")

    # This route can be used for further processing if needed
    return render_template('payment_routes/success_payment.html', title="Payment Successful", restaurant_name=restaurant_name, res_unique_azz_id=res_unique_azz_id)

@app.route('/cancel_payment')
def cancel_payment():
    restaurant_name = session.get("restaurant_name", "restaurant_placeholder")
    
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
            'published': order['published']
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



################################### Guides ####################################

@app.route('/excel_guide', methods=['GET'])
def serve_excel_guide():
    return render_template("guides/excel_guide.html", title="Excel File Guide", restaurant_name="MOM AI Assistant")



    
if __name__ == '__main__':
    app.run(debug=True)


################ Binance For Future Use ################
    
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