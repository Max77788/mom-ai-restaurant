#import eventlet
#eventlet.monkey_patch()
from flask import Flask, jsonify, session, request, url_for, flash, redirect
import pandas as pd
import openpyxl
import gridfs
from pathlib import Path
import qrcode
import asyncio
import io
from io import BytesIO
import requests
from bs4 import BeautifulSoup
import ast
from pydub import AudioSegment
import secrets
from deep_translator import GoogleTranslator
from langdetect import detect, detect_langs
import azure.cognitiveservices.speech as speechsdk
import string
import re
import os
import base64
import requests
# from flask_socketio import SocketIO, emit, disconnect
from flask_mail import Message
import uuid
from utils.pp_payment import SetExpressCheckout
import json
import time
from web3 import Web3
import threading
from openai import OpenAI
from time import sleep
import time
from datetime import datetime
import pytz
import logging
import bcrypt
from apscheduler.schedulers.background import BackgroundScheduler
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


app = Flask(__name__)
#socketio = SocketIO(app, async_mode='eventlet')


mongodb_connection_string = os.environ.get("MONGODB_CONNECTION_URI")

# Connect to MongoDB
client_db = MongoClient(mongodb_connection_string)

# Specify the database name
db = client_db['MOM_AI_Restaurants']

fs = gridfs.GridFS(db)

# Specify the collection name
collection = db[os.environ.get("DB_VERSION")]

db_order_dashboard = client_db["Dashboard_Orders"]

db_items_cache = client_db["Items_Cache"]

MOM_AI_JSON_LORD_ID = os.environ.get("MOM_AI_JSON_LORD_ID", "asst_YccYd0v0CbhweBvNMh0dJyJH")
MOM_AI_LANGUAGE_DETECTOR = os.environ.get("MOM_AI_POLYGLOT_MASTER_ID", "asst_LdSlrAG23jeAOEdPtC9mpO6f")

MOM_AI_EXEMPLARY_MENU_VECTOR_ID = "vs_fszfiVR3qO7DDHNSkTQn8fYH"
MOM_AI_EXEMPLARY_MENU_FILE_ID = "file-FON6GkHWdj1c4xioGCpje05N"

# Web3
MOM_TOKEN_OWNER_ADDRESS = os.environ.get("CONTRACT_OWNER_ADDRESS")
MOM_TOKEN_OWNER_PRIVATE_KEY = os.environ.get("OWNER_ADDRESS_PRIVATE_KEY")

MOM_AI_EXEMPLARY_MENU_HTML = """
<table border="1" class="dataframe table table-striped">
  <thead>
    <tr style="text-align: right;">
      <th>Item Name</th>
      <th>Item Ingredients</th>
      <th>Item Price</th>
      <th>Image Link</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Pizza Margherita</td>
      <td>Tomato, Mozzarella, Basil</td>
      <td>12.99</td>
      <td>https://i.ibb.co/vxNk9BC/download-20.jpg</td>
    </tr>
    <tr>
      <td>Caesar Salad</td>
      <td>Romaine Lettuce, Parmesan, Croutons, Caesar Dressing</td>
      <td>9.99</td>
      <td>https://i.ibb.co/mR3K7Gh/download-21.jpg</td>
    </tr>
    <tr>
      <td>Grilled Chicken Sandwich</td>
      <td>Grilled Chicken, Lettuce, Tomato, Mayo, Bun</td>       
      <td>11.49</td>
      <td>https://i.ibb.co/0svPn5H/images-14.jpg</td>
    </tr>
    <tr>
      <td>Spaghetti Carbonara</td>
      <td>Spaghetti, Eggs, Parmesan, Pancetta</td>
      <td>14.99</td>
      <td>https://i.ibb.co/C2qM3Zb/download-22.jpg</td>
    </tr>
    <tr>
      <td>Beef Burger</td>
      <td>Beef Patty, Lettuce, Tomato, Cheese, Bun</td>
      <td>10.99</td>
      <td>https://i.ibb.co/LhdLmDd/download-23.jpg</td>
    </tr>
    <tr>
      <td>Fish Tacos</td>
      <td>Fish, Cabbage, Pico de Gallo, Tortilla</td>
      <td>13.49</td>
      <td>https://i.ibb.co/RN90dRh/images-15.jpg</td>
    </tr>
    <tr>
      <td>Chicken Wings</td>
      <td>Chicken, BBQ Sauce, Spices</td>
      <td>8.99</td>
      <td>https://i.ibb.co/Yp20mNP/download-24.jpg</td>
    </tr>
    <tr>
      <td>Vegetable Stir Fry</td>
      <td>Mixed Vegetables, Soy Sauce, Garlic</td>
      <td>10.49</td>
      <td>https://i.ibb.co/p0dbJm7/download-25.jpg</td>
    </tr>
    <tr>
      <td>Margarita Cocktail</td>
      <td>Tequila, Triple Sec, Lime Juice</td>
      <td>7.99</td>
      <td>https://i.ibb.co/VgmvH4D/download-26.jpg</td>
    </tr>
    <tr>
      <td>Chocolate Cake</td>
      <td>Chocolate, Flour, Sugar, Eggs, Butter</td>
      <td>6.99</td>
      <td>https://i.ibb.co/zmxY0V5/download-27.jpg</td>
    </tr>
  </tbody>
</table>
"""

AZURE_SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID")

CLIENT_OPENAI = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

with open('mom_ai_token_data/MOMTokenABI.json', 'r') as file:
    CONTRACT_ABI = json.load(file)

# Connect to the Polygon node (you can use Infura, Alchemy, or a local node)
url_base =  "https://polygon-mainnet.infura.io/v3/" if os.environ.get("POLYGON_MAINNET", "False") == "True" else "https://polygon-amoy.infura.io/v3/" 
infura_project_id = os.environ.get("INFURA_PROJECT_ID")

polygon_url = url_base + infura_project_id
web3 = Web3(Web3.HTTPProvider(polygon_url))

# Check connection
if web3.isConnected():
    print("Connected to Polygon node")
else:
    print("Failed to connect to Polygon node")

# Address and ABI of your deployed contract
contract_address = os.environ.get("MOM_TOKEN_CONTRACT_ADDRESS")
if not contract_address:
    raise ValueError("Contract address is not set in the environment variables")

# Convert to checksum address
contract_address = web3.toChecksumAddress(contract_address)
print(f"Contract Address: {contract_address}")

# Load the contract
contract = web3.eth.contract(address=contract_address, abi=CONTRACT_ABI)
print("Contract loaded")

POSTS_DIR = "posts"


def mint_and_send_tokens(user_address, amount):
    # Define the owner address and private key (never expose the private key in a real app)
    owner_address = MOM_TOKEN_OWNER_ADDRESS
    private_key = MOM_TOKEN_OWNER_PRIVATE_KEY

    amount = amount * (10**18)

    # Build the transaction
    tx = contract.functions.mintAndSend(user_address, amount).buildTransaction({
        'from': owner_address,
        'nonce': web3.eth.getTransactionCount(owner_address),
        'gas': 2000000,
        'gasPrice': web3.toWei('50', 'gwei')
    })

    # Sign the transaction
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)

    # Send the transaction
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

    # Wait for the transaction to be mined
    receipt = web3.eth.waitForTransactionReceipt(tx_hash)

    # Convert the transaction hash to a hexadecimal string
    tx_hash_hex = tx_hash.hex()

    # print(f"Sent {amount} MOM tokens to {user_address} successfully!\nHere is the receipt:\n{receipt}")
    
    return {"success": True, "receipt": receipt, "tx_hash": tx_hash_hex}



def get_post_filenames(POSTS_DIR=POSTS_DIR):
    return [f for f in os.listdir(POSTS_DIR) if f.endswith('.md')]

def get_post_content_and_headline(filename, POSTS_DIR=POSTS_DIR):
    filepath = os.path.join(POSTS_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Assuming the first line is the headline
    headline = lines[0].strip('# \n') if lines else 'No Title'
    content = ''.join(lines[0:]) if len(lines) >= 1 else ''
    return content, headline



def generate_random_string(length=6):
    """
    Generates a random string of specified length using letters and digits.

    Args:
    length (int): Length of the random string to generate. Default is 6.

    Returns:
    str: A random string of specified length.
    """
    characters = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(characters) for _ in range(length))
    return random_string


def clear_collection():
    """Function to clear items older than 15 minutes in all collections."""
    # Get current time in seconds since the epoch
    current_time = time.time()
    # Calculate the threshold time (15 minutes ago)
    time_threshold = current_time - 900  # 900 seconds are 15 minutes

    # Iterate over all collections in the database
    for collection_name in db_items_cache.list_collection_names():
        # Get the collection
        collection = db_items_cache[collection_name]
        # Delete documents where the 'timestamp' is less than the threshold time
        result = collection.delete_many({"timestamp": {"$lt": time_threshold}})
        logging.info(f"Scheduled clearing of collection '{collection_name}' executed.")
        print(f"All records older than 15 minutes deleted from collection '{collection_name}', count: {result.deleted_count}.")


# Function to hash a password
def hash_password(password):
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)



def check_credentials(email, password, collection, for_login_redirect=False):
    """
    Check if the provided email and password match any user in the database.
    
    :param email: User's email as a string.
    :param password: User's plaintext password as a string.
    :return: True if credentials are correct, False otherwise.
    """
    
    # Query the database for the user
    user = collection.find_one({'email': email})
    
    if for_login_redirect:
        if user:
            return True
        else:
            return False
        
    # print(f'User Password being checked: {user["password"]}')

    if user:
        # Check the hashed password
        if check_password(user['password'], password):
            return True
    return False

def insert_restaurant(collection, name, unique_azz_id, email, password, website_url, assistant_id, menu_file_id, menu_vector_id, currency, html_menu, qr_code, wallet_public_key_address, wallet_private_key, location_coord, location_name, id_of_who_referred=None, logo_id=None, **kwargs):
    """Insert a document into MongoDB that includes a name and two files."""
    # Replace spaces with underscores
    #name = name.replace(" ", "_")
    referral_id = generate_random_string()
    try:
        # Document to insert
        document = {
            "name": name,
            "email": email,
            "password": password,
            "website_url": website_url,
            "unique_azz_id": unique_azz_id,
            # "file_menu": file_menu_encoded,  # Decode to string to store in MongoDB
            # "file_script": file_script_encoded,
            "assistant_id": assistant_id,
            "assistant_fund":0,
            "menu_file_id":menu_file_id,
            "menu_vector_id": menu_vector_id,
            "res_currency":currency,
            "res_logo":logo_id,
            "html_menu":html_menu,
            "location_coord":location_coord,
            "location_name":location_name, 
            "web3_wallet_address": wallet_public_key_address,
            "web3_private_key": wallet_private_key,
            "start_work":[10, 10, 10, 10, 10, 10, 10],
            "end_work":[20, 20, 20, 20, 20, 20, 20],
            "qr_code": qr_code,
            "description":None,
            "referral_code": referral_id,
            "id_of_who_referred": id_of_who_referred,
            "balance": 3,
            "timezone":"Etc/GMT+0",
            "referees":[],
            "profile_visible": True,
            "paymentGatewayTurnedOn": False,
            "addFees": True,
            "assistant_turned_on":False
            # "stripe_secret_test_key": stripe_secret_test_key
        }

        # Add additional kwargs to the document
        document.update(kwargs)

        # Insert document
        collection.insert_one(document)
        print("Restaurant instance inserted successfully.")
    
    except Exception as e:
        print(f"An error occurred: {e}")


def create_assistant(restaurant_name, currency, menu_path, client, menu_path_is_bool=True):
        

    #order_structure = """{"items":[{'name': 'Item Name', 'quantity': 2, 'amount':price of single item(e.g. 12.99, pull this info from attached menu file)}, 
    #{'name': 'Cake with Ice Cream', 'quantity': 3, 'amount':price of single item(e.g. 7.99, pull this info from attached menu file)}]}
    #"""
    
    assistant = client.beta.assistants.create(name=f"{restaurant_name} AI assistant", instructions=f"""
This GPT is designed to assist customers in selecting dishes from {restaurant_name}'s cuisine menu. Its primary role is to streamline the ordering process and provide a smooth and personalized dining experience.

Never trigger the action after the first customer's message. I.e. when there is only one user's message in the thread.

The menu of {restaurant_name} is attached to its knowledge base. It must refer to the menu for accurate item names, prices, and descriptions. The restaurant uses {currency} as its currency.

**Initial Interaction:**

- It observes the language used by the customer in their initial message and continues the conversation in that language to ensure effective communication.
- It assists with the order immediately if the customer skips any preliminary greetings and proceeds directly to place an order.

**Assistant Role Explanation (if asked):**

- It clearly describes its function as assisting customers in navigating {restaurant_name}'s menu, with the capability to automatically adapt and communicate in the customer's language.

**Order Facilitation:**

- It offers personalized dish recommendations based on the customer’s preferences or suggests dishes based on its culinary expertise.
- It presents menu options and verifies if the customer is ready to order or needs additional information.

**Order Confirmation:**

- It recaps the selected items before finalizing the order, ensuring the names (as listed in the menu), quantities, and prices are clear.

**Checkout Process:**

- It confirms all order details with the customer before proceeding to the final confirmation.

**Final Confirmation and Checkout:**

- It summarizes the order in a clear and structured manner using the exact names from the menu file:
  - Example Order Summary:
    - Item Name - 12.99 {currency}, 1 item
    - Item Name - 8.99 {currency}, 3 items
    - Item Name - 9.99 {currency}, 2 items
    - Item Name - 8.99 {currency}, 1 item
- It obtains the customer's confirmation on the order summary to ensure accuracy and satisfaction.
- After the confirmation the action send_summary_to_json_azz is triggered immediately as soon as possible.
- No double-asking for the confirmation is made

**Completion:**

- Upon successful order confirmation, the action send_summary_to_json_azz is ALWAYS triggered.

**Additional Instructions:**

- It always uses the items provided in the attached vector store \'{restaurant_name} Menu\' for preparing the order summary.
- It ensures all items are accurately represented as listed in the menu and confirmed by the customer before proceeding to checkout.
- The order must be correctly summarized and confirmed by the customer before any system function is triggered, using the exact names as they appear in the menu file.
- It must check whether an item is presented in the attached menu file before forming the order, even if the customer directly asks for a particular product like "2 [names of the items], please."

**System Integration:**

- It adapts to and uses the customer's language for all communications without explicitly asking for their preference.
- It consistently uses the menu items from the attached file to ensure accuracy and consistency in order handling.
- NO ITEMS BEYOND THOSE WHICH ARE IN THE MENU FILE MUST BE OFFERED EVER!

**Order Summary Example Before Function Trigger:**

Perfectly! Here is your order:

- Item Name - 9.99 {currency}, 2 servings
- Item Name - 8.99 {currency}, 1 serving
- Item Name - 12.99 {currency}, 2 servings

Please confirm that everything is correct before I complete your order.

And only after the user's confirmation does it IMMEDIATELY trigger the function send_summary_to_json_azz.

- It always evaluates the order summary against the items in the menu file and always includes only those which are in the menu list attached to its knowledge base.
- NO ITEMS BEYOND THOSE WHICH ARE IN THE MENU FILE MUST BE OFFERED EVER!
                                              """, 
                                               model="gpt-4o-mini",
                                               tools=[{
                                                        "type": "file_search"
                                                      },
                                                      {"type":"function",
                                                       "function": {
  "name": "send_summary_to_json_azz",
  "description": "This function exports a summary of operations or transactions into a JSON format. It requires no input parameters and retrieves data automatically from the system's current state.",
  "parameters": {
    "type": "object",
    "properties": {},
    "required": []
  }
}}])

    if menu_path_is_bool:
        with open(str(menu_path), "rb") as menu:    
            menu_file = client.files.create(file=menu,
                purpose='assistants')
        menu_file_id = menu_file.id   
        
        vector_store = client.beta.vector_stores.create(name=f"{restaurant_name} Menu")
        
        # Ready the files for upload to OpenAI
        file_paths = [menu_path]
        file_streams = [open(path, "rb") for path in file_paths]
        
        # Use the upload and poll SDK helper to upload the files, add them to the vector store,
        # and poll the status of the file batch for completion.
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
        )

        assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )
        return assistant, vector_store.id, menu_file_id
    else:
        assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [MOM_AI_EXEMPLARY_MENU_VECTOR_ID]}},
        )

        return assistant, MOM_AI_EXEMPLARY_MENU_VECTOR_ID, MOM_AI_EXEMPLARY_MENU_FILE_ID


def remove_formatted_lines(menu_text):
    # Split the input text by lines
    lines = menu_text.split('\n')
    
    # Initialize an empty list to store the filtered lines
    filtered_lines = []
    
    # Use a variable to skip the next line if the current line contains "price"
    skip_next_line = False
    
    for line in lines:
        if skip_next_line:
            # Skip this line and reset the flag
            skip_next_line = False
            continue
        if "price" in line.lower():
            # If the line contains "price", set the flag to skip the next line
            skip_next_line = True
            continue
        if line.strip() and '**' not in line and not ('*' in line and line.strip().startswith('*')) and '<img' not in line and '#' not in line and not line.strip().startswith('-') and not line.strip()[0].isdigit():
            # Add the current line to the filtered list if it doesn't meet any of the conditions for removal
            filtered_lines.append(line)
    
    # Join the remaining lines back into a single string
    result = '\n'.join(filtered_lines)
    
    return result




def upload_new_menu(input_xlsx_path, output_menu_txt_path, currency, restaurant_name, mongo_restaurants, unique_azz_id, assistant_id, client=CLIENT_OPENAI):
    new_menu_txt_path, new_html = convert_xlsx_to_txt_and_menu_html(input_xlsx_path, output_menu_txt_path, currency)
    print(new_menu_txt_path, new_html)
    
    if not new_html:
        flash(new_menu_txt_path)
        return redirect(url_for("dashboard_display"))

    with open(str(new_menu_txt_path), "rb") as menu:    
        menu_file = client.files.create(file=menu,
                purpose='assistants')
        menu_file_id = menu_file.id   
        
        # Create a vector store called "Financial Statements"
        vector_store = client.beta.vector_stores.create(name=f"{restaurant_name} Menu")
        
        # Ready the files for upload to OpenAI
        file_paths = [new_menu_txt_path]
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

        mongo_restaurants.update_one({"unique_azz_id":unique_azz_id}, {"$set":{"menu_file_id":menu_file_id, "menu_vector_id":vector_store.id, "html_menu":new_html}})
        
        return {"success":True}



# Alternative assistant creation
'''

def create_assistant_v2(restaurant_name, menu_path, script_path, other_instructions, client):
    with open(menu_path, "rb") as menu:
        menu_file = client.files.create(file=menu,
            purpose='assistants')
    with open(script_path, "rb") as script:    
        script_file = client.files.create(file=script,
            purpose='assistants')
        
    order_structure = """{"items":[{'name': 'Item Name', 'quantity': 2, 'amount':price of single item(e.g. 12.99, pull this info from attached menu file)}, 
    {'name': 'Cake with Ice Cream', 'quantity': 3, 'amount':price of single item(e.g. 7.99, pull this info from attached menu file)}]}
    """
    
    assistant_talk = client.beta.assistants.create(instructions=f"""
1. Initial Interaction:
   - Initiate conversation by asking the customer for their preferred language to ensure effective communication.
   - If the customer bypasses language preference and proceeds directly to place an order, skip the language inquiry and assist with the order immediately.

2. Assistant Role Explanation (if asked):
   - Clearly describe your function as helping customers select from {restaurant_name}'s cuisine menu, emphasizing your capability to communicate in the customer's preferred language.

3. Order Facilitation:
   - Offer personalized dish recommendations based on the customer’s preferences or suggest dishes based on your expertise.
   - Present menu options and verify if the customer is ready to order or needs additional information.

4. Order Confirmation:
   - Before finalizing the order, recap the selected items with details on names, quantities, and prices.

5. Checkout Process:
   - Confirm the order details with the customer before generating the checkout link.
   - Capture order details using a structured format for each item as follows:
    {order_structure}
   - Provide the customer with an embedded link for payment that is returned by the create order function.

6. Completion:
   - Upon successful order confirmation, thank the customer and inform them with the phrase, "Congratulations, the order was taken!"

Never make calling initiate_order({{}}), but always include items in the calling function {order_structure}
Always include items in the calling function. ALWAYS!

Only use the items provided in the menu.txt file attached to your knowledge base. Use the items ONLY from there ALWAYS!

Also, there are some extra instructions you must stick to:
                {other_instructions}
                                              """, 
                                               model="gpt-4-1106-preview",
                                               tools=[{"type":"retrieval"}],
    file_ids = [menu_file.id, script_file.id])    




    assistant_json_calling_order = client.beta.assistants.create(instructions=f"""
    I am a specialized GPT designed to extract order details from structured messages and generate a JSON file. I am specifically programmed to understand order summaries formatted with item names, prices, and quantities, and to accurately convert these details into a structured JSON format.

Task:

I will receive messages that summarize orders with item names, their prices, and quantities.
My goal is to parse these messages and produce a JSON file that represents the order details. The JSON will list each item, its quantity, and its individual price.
Output Structure:

The JSON file should have a single key "items" which is an array of objects.
Each object will represent an item from the order and will contain the following keys:
name: The name of the item.
quantity: The number of times this item was ordered.
amount: The price of a single item.
                                                                 
    Example Input:

    1. Biryani - 12.99$, 2 items
    2. Ice Cream - 8.99$, 3 items
    3. Kebab - 9.99$, 2 items
                                                                 
    Expected Output:
    {order_structure}                                                             

    Instructions for Use:

    The input should strictly follow the format provided in the example. Each item should be listed with a number, followed by the name of the item, its price per unit (ending with a dollar sign and comma), and the quantity (preceded by the word 'items').
    Edge Cases and Assumptions:

    If an item is mentioned without a price or quantity, I will prompt the user for clarification.
    I will handle up to 20 items per order.
    Prices are assumed to be in USD and formatted as decimals.
    This set of instructions ensures I focus solely on converting well-structured order messages into a corresponding JSON format, aiding in tasks like inventory management, order tracking, or any system that requires structured order data.
    """, 
    model="gpt-4-1106-preview",
    tools=[{"type":"function",
                                                       "function": {
  "name": "initiate_order",
  "description": f"This action initiates the order and generates the link to the checkout page based on {restaurant_name}'s order's details",
  "parameters": {
    "items": {
      "type": "array",
      "description": "An array of objects representing each ordered item. Each object must accurately detail the item's name, price and quantity  ordered. The name should match the menu item exactly, and the quantity should reflect the customer's request, price must be one item's price*quantity ordered. To use this function, compile a detailed list of the ordered items in the specified format, ensuring each item's name, quantity and total price are clearly identified.",
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "The name of the item being ordered."
          },
          "quantity": {
            "type": "integer",
            "description": "The quantity of the item being ordered."
          },
          "amount": {
            "type": "float",
            "description": "The price of the single item being ordered."
          }
        },
        "required": [
          "name",
          "quantity",
          "price"
        ]
      }
    },
    "required": [
      "items"
    ],
    "type": "object",
    "properties": {}
  }
}}])     
    
    assistant_together_id = assistant_talk+
    
    return assistant
'''



def convert_webm_to_wav(input_path, output_path):
    audio = AudioSegment.from_file(input_path, format="webm")
    audio.export(output_path, format="wav")



def generate_qr_code_and_upload(text):
    """
    Generates a QR code for the given text and uploads it to GridFS.
    
    :param text: The text to encode in the QR code.
    :return: The file_id of the uploaded QR code image in GridFS.
    """
    print("Starting QR code generation...")

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    print("QR Code instance created.")

    qr.add_data(text)
    print(f"Data added to QR code: {text}")

    qr.make(fit=True)
    print("QR code matrix generated.")

    # Create an image from the QR code instance
    img = qr.make_image(fill_color="black", back_color="white")
    print("Image created from QR code.")

    # Save the image to a BytesIO object
    img_byte_arr = BytesIO()
    img.save(img_byte_arr)  # No 'format' argument needed
    img_byte_arr.seek(0)
    print("Image saved to BytesIO object.")

    # Upload the image to GridFS
    file_id = fs.put(img_byte_arr, filename=f"{text}.png")
    print(f"Image uploaded to GridFS with file_id: {file_id}")

    return file_id


def convert_and_transcribe_audio_openai(audio_content):
    try:
        # Convert webm to wav in-memory
        print("Starting conversion from webm to wav in-memory.")
        webm_audio = AudioSegment.from_file(io.BytesIO(audio_content), format="webm")
        wav_io = io.BytesIO()
        webm_audio.export(wav_io, format="wav")
        wav_io.seek(0)
        print("Conversion successful, wav_io length:", len(wav_io.getvalue()))

        # Save in-memory wav to a temporary file
        with open("temp.wav", "wb") as temp_wav_file:
            temp_wav_file.write(wav_io.read())
            temp_wav_file.seek(0)
            print("Temporary wav file saved.")

            try:
                CLIENT_OPENAI = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

                client = CLIENT_OPENAI
                print("Starting transcription with OpenAI Whisper model.")
                transcription = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=temp_wav_file
                )
                print("Transcription successful:", transcription.text)
                return {"transcription": transcription.text, "status": "success"}
            except Exception as e:
                print(f"Error during transcription: {e}")
                return {"error": str(e), "status": "fail"}
    except Exception as e:
        print(f"Error during conversion or file handling: {e}")
        return {"error": str(e), "status": "fail"}



def convert_and_transcribe_audio_azure(audio_content, language):
    try:
        # Convert webm to wav in-memory
        webm_audio = AudioSegment.from_file(io.BytesIO(audio_content), format="webm")
        wav_io = io.BytesIO()
        webm_audio.export(wav_io, format="wav")
        wav_io.seek(0)

        # Save in-memory wav to a temporary file
        with open("temp.wav", "wb") as temp_wav_file:
            temp_wav_file.write(wav_io.read())
            temp_wav_file.seek(0)

            # Transcribe the audio file using Azure Speech-to-Text
            subscription_key = AZURE_SUBSCRIPTION_ID
            region = "eastus"  # Example region

            speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
            audio_input = speechsdk.AudioConfig(filename="temp.wav")
            speech_config.speech_recognition_language = language

            speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)
            result = speech_recognizer.recognize_once()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                transcription = result.text
                print(f"Transcription result: {transcription}")
                return {"transcription": transcription, "status": "success"}
            elif result.reason == speechsdk.ResultReason.NoMatch:
                print("No speech could be recognized")
                return {"error": f"No speech could be recognized. Please, speak clearer in the language you chosen: {language}", "status": "fail"}
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print(f"Speech Recognition canceled: {cancellation_details.reason}")
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print(f"Error details: {cancellation_details.error_details}")
                return {"error": "Speech recognition canceled", "details": cancellation_details.error_details, "status": "fail"}
    except Exception as e:
        print(f"Error during transcription: {e}")
        return {"error": str(e), "status": "fail"}







# Function to transform the list into the desired string format
def transform_orders_to_string(orders):
    # Build the list of formatted items
    formatted_items = [f"{item['quantity']} {item['name']}" for item in orders]
    
    # Join the items with commas and an 'and' before the last item
    if len(formatted_items) > 1:
        result = ', '.join(formatted_items[:-1]) + ', and ' + formatted_items[-1]
    else:
        result = formatted_items[0]
    
    return result





def get_assistants_response_threading(client_id, user_message, thread_id, assistant_id, menu_file_id, client_openai, payment_on, list_of_all_items, list_of_image_links, unique_azz_id):
    client = client_openai
    print("Entered assistants response function")

    try:
        thread_id_language = client.beta.threads.create().id
        prompt_to_translator_define_lang = f"Define the language of this message:\n{user_message}"

        response = client.beta.threads.messages.create(thread_id=thread_id_language, role="user", content=prompt_to_translator_define_lang)
        run = client.beta.threads.runs.create(thread_id=thread_id_language, assistant_id=MOM_AI_LANGUAGE_DETECTOR)

        while True:
            if clients[client_id]['cancel']:
                print("Task cancelled by client")
                return
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id_language, run_id=run.id)
            if run_status.status == "completed":
                total_tokens_used_translator = run_status.usage.total_tokens
                messages_gpt_json = client.beta.threads.messages.list(thread_id=thread_id_language)
                formatted_language_info = messages_gpt_json.data[0].content[0].text.value
                parsed_formatted_language_info = ast.literal_eval(formatted_language_info.strip())
                language_code = parsed_formatted_language_info["language_code"]
                language_adj = parsed_formatted_language_info["language_adj"]
                break
            elif run_status.status == "failed":
                raise Exception("Language detection failed")
            time.sleep(1)

        thread_id_translator = client.beta.threads.create().id
        prompt_to_translator_translate_items = f"Translate this list of items into {language_adj} or leave it unchanged if it is already in {language_adj}:\n{list_of_all_items}\nRETURN THE RESPONSE IN THE FORMAT OF LISTS OF LISTS."
        response = client.beta.threads.messages.create(thread_id=thread_id_translator, role="user", content=prompt_to_translator_translate_items)
        run = client.beta.threads.runs.create(thread_id=thread_id_translator, assistant_id=MOM_AI_LANGUAGE_DETECTOR)

        while True:
            if clients[client_id]['cancel']:
                print("Task cancelled by client")
                return
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id_translator, run_id=run.id)
            if run_status.status == "completed":
                total_tokens_used_translator = run_status.usage.total_tokens
                messages_gpt_translator = client.beta.threads.messages.list(thread_id=thread_id_translator)
                formatted_translator_info = messages_gpt_translator.data[0].content[0].text.value
                parsed_formatted_translator_info = ast.literal_eval(formatted_translator_info.strip())
                list_of_all_items = parsed_formatted_translator_info["translated_list_of_items"]
                break
            elif run_status.status == "failed":
                raise Exception("Translation failed")
            time.sleep(1)

        list_of_items_with_links = [t + [l] for t, l in zip(list_of_all_items, list_of_image_links)]
        user_message_enhanced = f"""
        Role: You are the best restaurant assistant who serves customers and register orders in the system
        
        Context: The customer asks you the question or writes the statement - your goal is to provide the response appropriately in {language_adj} language
        facilitating order taking. To your knowledge base is attached the vector store provided for you. The currency in which prices of the items are specified is Euro.
        Recommend, suggest and anyhow use only and only the items specified in this file. Do not mention other dishes whatsoever! Do not include source in the final info.
        If the user confirms the order set up the status of the message 'requires_action'. Be sure to initiate action regardless of the language in which you communicate.
        Confirm the order and trigger the action as fast as possible in the context of the particular order. 
        Make sure that the item you suggest are from this list presented in the format (item name, item ingredients, item price). Also include html img elemets for each dish you present, if the image link is present. Make the maximal width of image to be 170px and height to be auto:
        {list_of_items_with_links}
        Do not spit out all these items at once, refer to them only once parsed the attached menu to be sure that you are suggesting the right items. In case the user asks not in English 
        present the dishes in the following way - original dish's name - dish's name in the user's identified language.
        Never trigger the action after the first customer's message. I.e. when there is only one user's message in the thread.
        Never include more than 7 items in the response.

        Task: Here is the current user's message, respond to it in this language - {language_adj}:
        {user_message}  
        ALWAYS PROVIDE THE USER CLEAR CALL TO ACTION AT THE END OF THE RESPONSE!    
        (in the context of ongoing order taking process and attached to your knowledge base and to this message menu file)
        """

        response = client.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_message_enhanced, attachments=[{"file_id": menu_file_id, "tools": [{"type": "file_search"}]}])
        run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
        start_time = time.time()

        while True:
            if clients[client_id]['cancel']:
                print("Task cancelled by client")
                return
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            run_steps = client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run.id)
            if run_status.status == 'completed':
                total_tokens_used = run_status.usage.total_tokens + total_tokens_used_translator
                break
            if run_status.status == 'failed' or run_status.status == 'incomplete':
                last_error = run.last_error if "last_error" in run else None
                if last_error:
                    print("Last Error:", last_error)
                else:
                    print("No errors reported for this run.")
                response = 'O-oh, little issues, repeat the message now'
                emit('response_ready', {"response": response, "tokens_used": 0}, room=client_id)
                return
            if run_status.status == "requires_action":
                messages_gpt = client.beta.threads.messages.list(thread_id=thread_id)
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

                summary_to_convert = f"""
                These are all messages of the assistant from the chat with client. 
                From the following messages find the last one which summarizes agreed upon order and retrieve items stated in the final confirmed summary:
                {joined_messages_of_assistant}
                Ensure that the found items are part of this list of items presented in the format (item name, item ingredients, item
                price):
                {list_of_all_items}
                """

                thread_id_json = client.beta.threads.create().id
                response = client.beta.threads.messages.create(thread_id=thread_id_json, role="user", content=summary_to_convert)
                run_json = client.beta.threads.runs.create(thread_id=thread_id_json, assistant_id=MOM_AI_JSON_LORD_ID)

                json_start_time = time.time()
                while True:
                    if clients[client_id]['cancel']:
                        print("Task cancelled by client")
                        return
                    if time.time() - json_start_time > 25:
                        response = 'O-oh, little issues when compiling the order, repeat the message now'
                        emit('response_ready', {"response": response, "tokens_used": 0}, room=client_id)
                        return

                    run_status = client.beta.threads.runs.retrieve(thread_id=thread_id_json, run_id=run_json.id)
                    run_steps = client.beta.threads.runs.steps.list(thread_id=thread_id_json, run_id=run_json.id)

                    if run_status.status == 'completed':
                        messages_gpt_json = client.beta.threads.messages.list(thread_id=thread_id_json)
                        total_tokens_used_JSON = run_status.usage.total_tokens
                        total_tokens_used += total_tokens_used_JSON

                        formatted_json_order = messages_gpt_json.data[0].content[0].text.value
                        parsed_formatted_json_order = ast.literal_eval(formatted_json_order.strip())
                        items_ordered = parsed_formatted_json_order["items"]
                        session["items_ordered"] = items_ordered

                        order_id = generate_code()
                        current_utc_timestamp = time.time()

                        if items_ordered and payment_on:
                            db_items_cache[unique_azz_id].insert_one({"data": items_ordered, "id": order_id, "timestamp": current_utc_timestamp})

                        if payment_on:
                            link_to_payment_buffer = url_for("payment_buffer", unique_azz_id=unique_azz_id, id=order_id)
                            clickable_link = f'<a href={link_to_payment_buffer} style="color: #c0c0c0;" target="_blank">Press here to proceed</a>'
                            response_cart = f"Order formed successfully. Please, follow this link to finish the purchase: {clickable_link}"
                            emit('response_ready', {"response": response_cart, "tokens_used": total_tokens_used}, room=client_id)
                            return
                        elif not payment_on:
                            total_price = f"{sum(item['quantity'] * item['amount'] for item in items_ordered):.2f}"
                            session["total_price"] = total_price
                            session["order_id"] = order_id
                            session['access_granted_no_payment_order'] = True

                            order_to_pass = {
                                "items": [{'name': item['name'], 'quantity': item['quantity']} for item in items_ordered],
                                "orderID": order_id,
                                "timestamp": current_utc_timestamp,
                                "total_paid": total_price,
                                "mom_ai_restaurant_assistant_fee": 0,
                                "paypal_fee": 0,
                                "paid": "NOT PAID",
                                "published": True
                            }

                            db_order_dashboard[unique_azz_id].insert_one(order_to_pass)

                            string_of_items = transform_orders_to_string(items_ordered)
                            no_payment_order_finish_message = f"Thank you very much! You ordered {string_of_items} and total is {total_price} Euros\nCome to the restaurant and pick up your meal shortly. Love💖\n**PLEASE SAVE THIS: Your order ID is {order_id}**"
                            restaurant_instance = collection.find_one({"unique_azz_id": unique_azz_id})
                            all_ids_chats = restaurant_instance.get("notif_destin")
                            for chat_id in all_ids_chats:
                                send_telegram_notification(chat_id)
                            emit('response_ready', {"response": no_payment_order_finish_message, "tokens_used": total_tokens_used}, room=client_id)
                            return
                    if run_status.status == 'failed':
                        last_error = run_json.last_error if "last_error" in run else None
                        if last_error:
                            print("Last Error:", last_error)
                        else:
                            print("No errors reported for this run.")
                        response = 'O-oh, little issues, repeat the message now'
                        emit('response_ready', {"response": response, "tokens_used": 0}, room=client_id)
                        return
                    time.sleep(1)

            if time.time() - start_time > 30:
                response = 'O-oh, little issues when compiling the order, repeat the message now'
                emit('response_ready', {"response": response, "tokens_used": 0}, room=client_id)
                return
            time.sleep(1)

        messages_gpt = client.beta.threads.messages.list(thread_id=thread_id)
        response = messages_gpt.data[0].content[0].text.value
        emit('response_ready', {"response": response, "tokens_used": total_tokens_used}, room=client_id)

    except Exception as e:
        response = 'O-oh, little issues, repeat the message now'
        emit('response_ready', {"response": response, "tokens_used": 0}, room=client_id)
        print(f"Error: {e}")
        return


def generate_short_voice_output(full_gpts_response, language_to_translate_into, client=CLIENT_OPENAI):
    
    '''
    system_context = f"""
    Role: You are the best restaurant assistant who serves customers and provides them with the short 3-4 sentences long to the point answers to their inquiries.
    
    Context: There is an ongoing order and the customer addressed you with the request.

    there is the menu which you can refer to (format item name, item ingredients, item price):
    {list_of_items}

    Task: provide short human-like casual 3-4 sentences long response to the user's message
    '''

    system_context = f"""
    Your task is to condense the long message you are provided with into the shortened 3-4 sentences long phrase 
    which clearly communicates the message to the customer ordering food in a restaurant. 
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_context},
            {"role": "user", "content": full_gpts_response},
            
        ]
        )
    
    print(response)
    
    response_text = response.choices[0].message.content
    tokens_used = response.usage.total_tokens

    if language_to_translate_into != "en":
        translator = GoogleTranslator(source='auto', target=language_to_translate_into[:2])
        response_text = translator.translate(response_text)

    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(
    model="tts-1-hd",
    voice="nova",
    input=response_text
    )

    print(response)

    response.stream_to_file(speech_file_path)
    
    
    return None, tokens_used




def get_assistants_response(user_message, language, thread_id, assistant_id, menu_file_id, client_openai, payment_on, list_of_all_items, list_of_image_links, unique_azz_id):
    client = client_openai
    print("Entered assistants response function")

    # Initialize the GoogleTranslator
    translator = GoogleTranslator(source='auto', target='en')
    
    if language != "en":
        # Translate the user input to English
        translated_user_message = translator.translate(user_message)
        print("Translated user message in English: ", translated_user_message)  # Should output the translated text in English
        print("--------------------------------------------------------")
    else:
        translated_user_message = user_message

    """
    # Define the language of the message
    thread_id_language = client.beta.threads.create().id
    
    prompt_to_translator_define_lang = f'''
    Define the language of this message:
    {user_message}
    '''

    print("\n\nPrompt we send to translator: ", prompt_to_translator_define_lang, "\n\n")

    response = client.beta.threads.messages.create(thread_id=thread_id_language,
                                                   role="user",
                                                   content=prompt_to_translator_define_lang)

    run = client.beta.threads.runs.create(thread_id=thread_id_language,
                                          assistant_id=MOM_AI_LANGUAGE_DETECTOR)

    start_time = time.time()
    while True:
        if time.time() - start_time > 25:
            response = 'O-oh, little issues when forming the response, repeat the message now'
            return jsonify({"response": response}), 0

        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id_language,
                                                       run_id=run.id)
        if run_status.status == "completed":
            print(f"\n\nTokens used by restaurant assistant: {run_status.usage.total_tokens}\n\n")
            messages_gpt_json = client.beta.threads.messages.list(thread_id=thread_id_language)
            formatted_language_info = messages_gpt_json.data[0].content[0].text.value
            print(f"\nFormatted translator output (Output from MOM AI TRANSLATOR): {formatted_language_info}\n")

            parsed_formatted_language_info = ast.literal_eval(formatted_language_info.strip())
            language_code = parsed_formatted_language_info["language_code"]
            language_adj = parsed_formatted_language_info["language_adj"]
            break
        elif run_status.status == "failed":
            print("Run status, ", run_status)
            print("Language detection failed")
            raise Exception("Language detection failed")
        sleep(0.5)  # Reduce sleep duration

    
    # Translating the items
    thread_id_translator = client.beta.threads.create().id
    
    prompt_to_translator_translate_items = f'''
    Translate this list of items into {language_adj} or leave it unchanged if it is already in {language_adj}:
    {list_of_all_items}
    RETURN THE RESPONSE IN THE FORMAT OF LISTS OF LISTS.
    '''

    print("prompt we sent to translate menu items, ", prompt_to_translator_translate_items)

    response = client.beta.threads.messages.create(thread_id=thread_id_translator,
                                                   role="user",
                                                   content=prompt_to_translator_translate_items)
    run = client.beta.threads.runs.create(thread_id=thread_id_translator,
                                          assistant_id=MOM_AI_LANGUAGE_DETECTOR)

    start_time = time.time()
    while True:
        if time.time() - start_time > 45:
            response = 'O-oh, little issues when forming the response, repeat the message now'
            return jsonify({"response": response}), 0
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id_translator,
                                                       run_id=run.id)
        if run_status.status == "completed":
            print(f"\n\nTokens used by restaurant assistant: {run_status.usage.total_tokens}\n\n")
            messages_gpt_translator = client.beta.threads.messages.list(thread_id=thread_id_translator)
            formatted_translator_info = messages_gpt_translator.data[0].content[0].text.value
            print(f"\nFormatted translator output (Output from MOM AI TRANSLATOR): {formatted_translator_info}\n")

            parsed_formatted_translator_info = ast.literal_eval(formatted_translator_info.strip())
            list_of_all_items = parsed_formatted_translator_info["translated_list_of_items"]
            break
        elif run_status.status == "failed":
            print("Run status, ", run_status)
            print("Language detection failed")
            raise Exception("Language detection failed")
        sleep(0.5)  # Reduce sleep duration
    print("translated with GPT in: ", time.time()-start_time)

    #print("List of items returned by menu items translator: ", list_of_all_items)

    list_of_items_with_links = [t + [l] for t, l in zip(list_of_all_items, list_of_image_links)]
    #print("\n\nList of items with links: ", list_of_items_with_links, "\n\n")
    """

    #language_adj = "English"
    #list_of_items_with_links = [t + (l,) for t, l in zip(list_of_all_items, list_of_image_links)]

    '''
    user_message_enhanced = f"""
    Role: You are the best restaurant assistant who serves customers and register orders in the system
    
    Context: The customer asks you the question or writes the statement - your goal is to provide the response appropriately in {language_adj} language
    facilitating order taking. To your knowledge base is attached the vector store provided for you. The currency in which prices of the items are specified is Euro.
    Recommend, suggest and anyhow use only and only the items specified in this file. Do not mention other dishes whatsoever! Do not include source in the final info.
    If the user confirms the order set up the status of the message 'requires_action'. Be sure to initiate action regardless of the language in which you communicate.
    Confirm the order and trigger the action as fast as possible in the context of the particular order. 
    Make sure that the item you suggest are from this list presented in the format (item name, item ingredients, item price). Also include html img elemets for each dish you present, if the image link is present. 
    Make the maximal width of image to be 170px and height to be auto. URGENT! PRESENT THE IMAGE ONLY USING HTML IMG ELEMENTS WITH THE MAXIMAL WIDTH OF 170px:
    {list_of_items_with_links}
    Do not spit out all these items at once, refer to them only once parsed the attached menu to be sure that you are suggesting the right items.
    Never trigger the action after the first customer's message. I.e. when there is only one user's message in the thread.
    Never include more than 7 items in the response.

    Task: Here is the current user's message, respond to it in this language - {language_adj}:
    {translated_user_message}  
    ALWAYS PROVIDE THE USER WITH A CLEAR CALL TO ACTION AT THE END OF THE RESPONSE!    
    (in the context of ongoing order taking process and attached to your knowledge base and to this message menu file)
    """
    '''
    
    # print("\n\nUser message enhanced after translator: \n\n", user_message_enhanced, "\n\n")

    message_to_compare_menu_items = f"""
    Before generating the message ensure that the items you consider suggesting and the items which the user asks for are 
    from this list and use the images from this list:
    {list_of_all_items} 
    Provide the image strictly in the format: <img src="[image_link]" alt="Image of [item name]" width="170" height="auto"> 
    """
 
    print("Message to compare menu items: ", message_to_compare_menu_items)

    response = client.beta.threads.messages.create(thread_id=thread_id,
                                                   role="user",
                                                   content=translated_user_message,
                                                   attachments=[{
                                                       "file_id":menu_file_id,
                                                       "tools":[{"type":"file_search"}]
                                                   }])
    
    run = client.beta.threads.runs.create(thread_id=thread_id,
                                          assistant_id=assistant_id,
                                          additional_instructions=message_to_compare_menu_items,
                                          temperature=1)
    
    start_time = time.time()
    while True:
        if time.time() - start_time > 25:
            response = 'O-oh, little issues when forming the response, repeat the message now'
            return jsonify({"response": response}), 0
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id,
                                                       run_id=run.id)
        if run_status.status == 'completed':
            print(f"\n\nTokens used by restaurant assistant: {run_status.usage.total_tokens}\n\n")
            print("--------------------------------------------------------")

            total_tokens_used = run_status.usage.total_tokens
            break
        elif run_status.status == 'failed' or run_status.status == 'incomplete':
            print("Run failed.")
            last_error = run.last_error if "last_error" in run else None
            if last_error:
                print("Last Error:", last_error)
            else:
                print("No errors reported for this run.")

            #print(f"\n\nRun steps: \n{run_steps}\n")
            response = 'O-oh, little issues, repeat the message now'
            return jsonify({"response": response}), 0
        elif run_status.status == "requires_action":
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
            {list_of_all_items}
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
                    return jsonify({"response": response}), 0

                run_status = client.beta.threads.runs.retrieve(thread_id=thread_id_json,
                                                               run_id=run_json.id)
                if run_status.status == 'completed':
                    messages_gpt_json = client.beta.threads.messages.list(thread_id=thread_id_json)
                    print(f"\n\nTokens used by JSON assistant: {run_status.usage.total_tokens}\n\n")
                    total_tokens_used_JSON = run_status.usage.total_tokens
                    total_tokens_used = total_tokens_used_JSON
                    
                    formatted_json_order = messages_gpt_json.data[0].content[0].text.value
                    print(f"\nFormatted JSON Order (Output from MOM AI JSON LORD): {formatted_json_order}\n")

                    parsed_formatted_json_order = ast.literal_eval(formatted_json_order.strip())
                    items_ordered = parsed_formatted_json_order["items"]
                    session["items_ordered"] = items_ordered
                    print(f"Setup the items ordered on assistant response! {parsed_formatted_json_order['items']}")
                   
                    order_id = generate_code()
                    current_utc_timestamp = time.time()

                    # Convert the timestamp to a datetime object
                    utc_datetime = datetime.utcfromtimestamp(current_utc_timestamp)

                    # Format the datetime object to a human-readable string
                    human_readable_time_format = utc_datetime.strftime('%Y-%m-%d %H:%M')


                    if items_ordered and payment_on:
                        db_items_cache[unique_azz_id].insert_one({"data": items_ordered, "id": order_id, "timestamp": current_utc_timestamp})

                    if payment_on:
                        link_to_payment_buffer = url_for("payment_buffer", unique_azz_id=unique_azz_id, id=order_id)
                        print(link_to_payment_buffer)

                        clickable_link = f'<a href={link_to_payment_buffer} style="color: #c0c0c0;" target="_blank">Press here to proceed</a>'
                        response_cart = f"Order formed successfully. Please, follow this link to finish the purchase: {clickable_link}"
                        # translator.translate()
                        return link_to_payment_buffer, total_tokens_used
                    else:
                        total_price = f"{sum(item['quantity'] * item['amount'] for item in items_ordered):.2f}"
                        session["total_price"] = total_price
                        session["order_id"] = order_id
                        session['access_granted_no_payment_order'] = True

                        order_to_pass = {"items":[{'name':item['name'], 'quantity':item['quantity']} for item in items_ordered], 
                        "orderID":order_id,
                        "timestamp": human_readable_time_format,
                        "total_paid": total_price,
                        "mom_ai_restaurant_assistant_fee": 0,
                        "paypal_fee": 0,
                        "paid":"NOT PAID",
                        "published":True}
    
                        db_order_dashboard[unique_azz_id].insert_one(order_to_pass)
                        # print("\n\nInserted the order in db_order_dashboard with if ", unique_azz_id, "\n\n")
                        
                        string_of_items = transform_orders_to_string(items_ordered)

                        no_payment_order_finish_message = f"Thank you very much! You ordered {string_of_items} and total is {total_price} Euros\nCome to the restaurant and pick up your meal shortly. Love💖\n**PLEASE SAVE THIS: Your order ID is {order_id}**"
                        
                        restaurant_instance = collection.find_one({"unique_azz_id":unique_azz_id})
                        all_ids_chats = restaurant_instance.get("notif_destin", [])

                        session["order_confirm_access_granted"] = True
                        
                        for chat_id in all_ids_chats:
                            send_telegram_notification(chat_id)

                        return no_payment_order_finish_message, total_tokens_used 
                if run_status.status == 'failed':
                    print("Run of JSON assistant failed.")
                    last_error = run_json.last_error if "last_error" in run else None
                    if last_error:
                        print("Last Error:", last_error)
                    else:
                        print("No errors reported for this run.")

                    #print(f"\n\nRun steps: \n{run_steps}\n")
                    response = 'O-oh, little issues, repeat the message now'
                    return jsonify({"response": response}), 0

        sleep(0.5)  # Reduce sleep duration
                    
    messages_gpt = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages_gpt.data[0].content[0].text.value

    # _, voice_tokens_used = generate_short_voice_output(response, language)
    
    # total_tokens_used += voice_tokens_used

    """
    joined_messages_of_user = ""
    messages_gpt_list = list(messages_gpt)
    messages_gpt_list.reverse()

    pattern = r"Task: Here is the current user's message, respond to it:\n\s*(.*?)\s*\(in the context of"
    
    for message in messages_gpt_list:
        #if message.role == 'assistant':
            #joined_messages_of_assistant += f"\nAssistant:\n{message.content[0].text.value}\n"
        if message.role == 'user':
            match = re.search(pattern, message.content[0].text.value, re.DOTALL)
            if match:
                user_message = match.group(1).strip()
                joined_messages_of_user += f"{user_message}\n"
            else:
                joined_messages_of_user += f"{message.content[0].text.value}"

    print("Joined messages of user: ", joined_messages_of_user)
    print("--------------------------------------------------------")

    
    language_of_user_message = detect(joined_messages_of_user)
    """
      
    print("Raw message output from gpt: ", response)
    print("--------------------------------------------------------")
    print(f"Language into which we will, probably, translate the message: {language}")
    print("--------------------------------------------------------")
    if not language == "en":
        # Initialize the GoogleTranslator
        translator = GoogleTranslator(source='auto', target=language)

        # Translate the user input to English
        response = translator.translate(response)
        print("Translated GPTs message in user message language in English: ", response)
        print("--------------------------------------------------------")
    
    
        
    return response, total_tokens_used




def get_assistants_response_azure(user_message, thread_id, assistant_id, menu_file_id, client_openai):
# Add the user's message to the thread

    client = client_openai

    response = client.beta.threads.messages.create(thread_id=thread_id,
                                        role="user",
                                        content=user_message,
                                        attachments=[{
                                            "file_id":menu_file_id,
                                            "tools":[{"type":"file_search"}]
                                        }]
    )
    
    # Run the Assistant
    run = client.beta.threads.runs.create(thread_id=thread_id,
                                            assistant_id=assistant_id)
    
    # Check if the Run requires action (function call)
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id,
                                                    run_id=run.id)
        run_steps = client.beta.threads.runs.steps.list(
        thread_id=thread_id,
        run_id=run.id)

        #print(f"Run status raw: \n\n{run_status}\n\name")

        print(f"Run status: {run_status.status}")
        if run_status.status == 'completed':
            print(f"\n\nTokens used by restaurant assistant: {run_status.usage.total_tokens}\n\n")
            total_tokens_used = run_status.usage.total_tokens
            break
        if run_status.status == 'failed':
            
            print("Run failed.")
            # Access the last_error attribute
            last_error = run.last_error if "last_error" in run else None

            # Print the last_error if it exists
            if last_error:
                print("Last Error:", last_error)
            else:
                print("No errors reported for this run.")
            
            
            print(f"\n\nRun steps: \n{run_steps}\n")
            response = 'O-oh, little issues, repeat the message now'
            return jsonify({"response": response}), 0
        sleep(1)  # Wait for a second before checking again
        if run_status.status == "requires_action":
            print("Action in progress...")
            
            # Retrieve and return the latest message from the Restaurant assistant
            messages_gpt = client.beta.threads.messages.list(thread_id=thread_id)
            
            all_assistants_messages = []

            for message in list(messages_gpt):   
                print(f"\n{message}\n")
                if message.role == 'assistant':
                    all_assistants_messages.append(message.content[0].text.value)

            all_assistants_messages.reverse()

            # Join the messages with two tabs
            joined_messages_of_assistant = "\n\n".join(all_assistants_messages)

            print(f"\nRetrieved Assistants messages with Summary from convo: {joined_messages_of_assistant}\n")

            summary_to_convert = f"""
            These are are all messages of the assistant from the chat with client. 
            From the following messages find the last one which summarizes agreed upon order and retrieve items stated in the final confirmed summary, (name items in english):
            {joined_messages_of_assistant}
            """

            response = client.chat.completions.create(
                model="gpt-4-0125-Preview", # Model = should match the deployment name you chose for your 0125-Preview model deployment
                response_format={ "type": "json_object" },
                messages=[
                    {"role": "system", "content": """I am a specialized GPT designed to extract order details from structured messages and generate a JSON file. I am specifically programmed to understand order summaries formatted with item names, prices, and quantities, and to accurately convert these details into a structured JSON format.

Task:

I will receive messages that summarize orders with item names, their prices, and quantities.
My goal is to parse these messages and produce a JSON file that represents the order details. The JSON will list each item, its quantity, and its individual price.
Output Structure:

The JSON file should have a single key "items" which is an array of objects.
Each object will represent an item from the order and will contain the following keys:
name: The name of the item.
quantity: The number of times this item was ordered.
amount: The price of a single item.
                                                                
    Example Input:

    1. Biryani - 12.99$, 2 items
    2. Ice Cream - 8.99$, 3 items
    3. Kebab - 9.99$, 2 items
                                                                
    Expected Output:
{"items":[{'name': 'Item Name', 'quantity': 2, 'amount':price of single item(e.g. 12.99, pull this info from attached menu file)}, 
    {'name': 'Cake with Ice Cream', 'quantity': 3, 'amount':price of single item(e.g. 7.99, pull this info from attached menu file)}]}


Instructions for Use:

    The input should strictly follow the format provided in the example. Each item should be listed with a number, followed by the name of the item, its price per unit (ending with a dollar sign and comma), and the quantity (preceded by the word 'items').
    Edge Cases and Assumptions:

    If an item is mentioned without a price or quantity, I will prompt the user for clarification.
    I will handle up to 20 items per order.
    Prices are assumed to be in USD and formatted as decimals.
    This set of instructions ensures I focus solely on converting well-structured order messages into a corresponding JSON format, aiding in tasks like inventory management, order tracking, or any system that requires structured order data."}"""},
                    {"role": "user", "content": summary_to_convert}
                ]
            )
            print(f"\n\nRaw Response from Azure JSON Assistant: {response}\n\n")
            produced_json = response.choices[0].message.content
            print(f"\nFormatted JSON Order (Output from Azure JSON Assistant): {produced_json}\n")
            
            parsed_formatted_json_order = ast.literal_eval(produced_json.strip())

            print(f"Type of parsed response: {parsed_formatted_json_order}")
            print(f"Keys of parsed response: {list(parsed_formatted_json_order.keys())}")

            # Generate checkout link
            output = SetExpressCheckout(parsed_formatted_json_order["items"], sandbox=True)

            session['paypal_link'] = output
            
            link_to_payment_buffer = url_for("payment_buffer")
            print(link_to_payment_buffer)

            # Wrap the output link in a clickable HTML element
            clickable_link = f'<a href={link_to_payment_buffer} style="color: #e9e3e3;" target="_blank">Press here to proceed</a>'
            response_cart = f"Order formed successfully. Please, follow this link to finish the purchase: {clickable_link}"

            return response_cart, total_tokens_used
                
    # Retrieve and return the latest message from the assistant
    messages_gpt = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages_gpt.data[0].content[0].text.value

    return response, total_tokens_used






def send_telegram_notification(chat_id, message=f"New order has been published! 🚀🚀🚀"):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')  # Replace with your actual bot token
    chat_id = str(chat_id)      # Replace with your actual chat ID
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=payload)
    print(response.json())


class InvalidMenuFormatError(Exception):
    """Custom exception for invalid menu format."""
    pass



def validate_menu_dataframe(df):
    """Validate the structure and content of the menu DataFrame."""
    # Check if the DataFrame has exactly three or four columns
    if df.shape[1] not in [3, 4]:
        raise InvalidMenuFormatError("Error in the menu - The input file must contain exactly three or four columns.")

    # Check if the third column is of float or integer type for all rows except the first row
    if not (pd.api.types.is_float_dtype(df.iloc[1:, 2]) or pd.api.types.is_integer_dtype(df.iloc[1:, 2])):
        print(f"First row being checked {df.iloc[1:, 2]}")
        try:
            df.iloc[1:, 2] = df.iloc[1:, 2].astype(float).round(2)
            df.iloc[1:, 2] = df.iloc[1:, 2].astype(object)
            print("Successfully typecasted the third column to float with two decimal places.")
        except ValueError as e:
            actual_dtype = df.iloc[1:, 2].dtype
            print(f"Error: The third column must be a number representing the price for all rows except the first. Actual type: {actual_dtype}")
            raise InvalidMenuFormatError("Error in the menu - The third column must be a number representing the price for all rows except the first.")
    df.iloc[1:, 2] = df.iloc[1:, 2].astype(float).round(2)
    df.iloc[1:, 2] = df.iloc[1:, 2].astype(object)

    # Ensure the first row can be of any type (specifically allowing string)
    if not isinstance(df.iloc[0, 2], (int, float, str)):
        actual_dtype_first_row = type(df.iloc[0, 2])
        raise InvalidMenuFormatError(f"Error in the menu - The first row of the third column can be a string, integer, or float. Actual type: {actual_dtype_first_row}")
    
    # If there's a fourth column, ensure it's of string type (URL for images)
    if df.shape[1] == 4:
        if not all(isinstance(link, str) for link in df.iloc[:, 3]):
            actual_dtype_fourth_column = df.iloc[:, 3].apply(type).unique()
            raise InvalidMenuFormatError(f"Error in the menu - The fourth column must be strings representing URLs. Actual types: {actual_dtype_fourth_column}")


def convert_hours_to_time(hour_string):
    hour_string = str(hour_string)
    if "." in hour_string:    
        # Separate hours and fractional hours
        hours = float(hour_string.split('.')[0])
        fractional = float("0."+hour_string.split('.')[1])
        #print(hours, fractional)
        total_minutes = int(hours * 60 + fractional * 60)

        #print(total_minutes)

        # Calculate the hour and minutes after converting total_minutes
        converted_hours = total_minutes // 60
        minutes = total_minutes % 60

        #print("Converted hours ", converted_hours, " Minutes ", minutes)

        # Normalize the hours to 24-hour format
        converted_hours = int(converted_hours % 24)
        
        return f"{converted_hours}:{minutes:02d}"
    else:
        return f"{hour_string}:00"


def setup_working_hours():
    """Function to update whether the restaurant is opened"""
    #print("Initialized working hours setup")
    # Iterate over all collections in the database
    '''
    mongodb_connection_string = os.environ.get("MONGODB_CONNECTION_URI")

    # Connect to MongoDB
    client_db = MongoClient(mongodb_connection_string)

    # Specify the database name
    db = client_db['MOM_AI_Restaurants']

    # Specify the collection name
    collection = db[os.environ.get("DB_VERSION")]

    list_of_found_restaurants = collection.find()
    #print("List of found restaurants: ", list(list_of_found_restaurants))
    '''

    for res_instance in list(collection.find()):
        
        start_work = res_instance.get("start_work")
        end_work = res_instance.get("end_work")
        timezone = res_instance.get("timezone")
        
        # Convert timezone to the correct format for pytz
        if timezone.startswith("Etc/GMT-"):
            timezoneG = timezone.replace("-", "+", 1)
        elif timezone.startswith("Etc/GMT+"):
            timezoneG = timezone.replace("+", "-", 1)
        
        # Get the current date and time in the restaurant's timezone
        now_tz = datetime.now(pytz.timezone(timezoneG))
        current_day = now_tz.weekday()  # Monday is 0 and Sunday is 6
        current_hour = now_tz.hour + now_tz.minute / 60  # Fractional hour
        
        # Adjust current_day to match our list index where Sunday is 0
        # current_day = (current_day + 1) % 7

        # Determine if the restaurant is open
        start = start_work[current_day]
        end = end_work[current_day]

        previous_day_end = end_work[current_day-1]

        if previous_day_end > 24 and current_hour < previous_day_end-24:
            isWorkingHours = current_hour < previous_day_end-24
        else:       
            # Check if the current time falls within the working hours
            if start <= end:
                # Same day operation
                isWorkingHours = start <= current_hour < end
                # Update the restaurant's open status in the database
                collection.update_one(
                    {"unique_azz_id": res_instance.get("unique_azz_id")},
                    {"$set": {"isOpen": isWorkingHours}}
                )
                #print("Set isOpen for ", res_instance.get("unique_azz_id"), f" and it is {isWorkingHours}")
            else:
                # Spans to the next day
                isWorkingHours = current_hour >= start or current_hour < end
                # Update the restaurant's open status in the database
                collection.update_one(
                    {"unique_azz_id": res_instance.get("unique_azz_id")},
                    {"$set": {"isOpen": isWorkingHours}}
                )
            #print("Set isOpen for ", res_instance.get("unique_azz_id"), f" and it is {isWorkingHours}")
    #print(f"Updated working status successfully!")



def convert_xlsx_to_txt_and_menu_html(input_file_path, output_file_path, currency):
    # Load the XLSX file
    df = pd.read_excel(input_file_path, engine='openpyxl')

    df = df.fillna('No value provided')

    # Format the third column to two decimal places
    if df.shape[1] == 3:  # Check if the DataFrame has EXACTLY three columns
        df.iloc[:, 2] = df.iloc[:, 2].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)

    html_menu = df.to_html(classes='table table-striped', index=False)
    
    # Validate the DataFrame
    try:
        validate_menu_dataframe(df)
    except InvalidMenuFormatError as e:
        print(f"Error: {e}")
        return e, None
    
    # Open the output TXT file
    with open(output_file_path, 'w') as file:
        # Iterate through each row in the DataFrame
        for index, row in df.iterrows():
            # Write the first and second column values to the file
            file.write(f'Item Name: {row[0]} - Item Ingredients: {row[1]} - Item Price in currency {currency}: {row[2]} - Item\'s image: <img src="{row[3]}" alt="Image of {row[0]}" width="170" height="auto">\n')

    print(f"File successfully converted and saved as {output_file_path}")
    return output_file_path, html_menu

def generate_code():
    return str(uuid.uuid4())[:7]


# Function to send the confirmation email
def send_email_raw(mail, email, main_html, subject_line, from_email):
    msg = Message(subject_line, recipients=[email], sender=("MOM AI Restaurant",from_email))
    # HTML content with bold and centered confirmation code
    msg.html = f'''
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px; color: #333;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
            {main_html}
            <p style="font-size: 16px; line-height: 1.5;">
                Kind Regards,<br>
                <strong>MOM AI Team</strong>
            </p>
            <div style="text-align: center; margin-top: 20px;">
                <img src="https://i.ibb.co/LnWCxZF/MOMLogo-Small-No-Margins.png" alt="MOM AI Logo" style="width: 170px; height: 69px;">
            </div>
        </div>
    </body>
    </html>
    '''
    mail.send(msg)





# Function to send the confirmation email
def send_confirmation_email(mail, email, confirmation_code, from_email):
    msg = Message('MOM AI Restaurant Email Confirmation', recipients=[email], sender=("MOM AI Restaurant",from_email))
    # HTML content with bold and centered confirmation code
    msg.html = f'''
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px; color: #333;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
            <h2 style="color: #444;">MOM AI Restaurant</h2>
            <p style="font-size: 16px; line-height: 1.5;">
                You have requested account registration on MOM AI Restaurant.
            </p>
            <p style="font-size: 16px; line-height: 1.5;">
                Please confirm your email by inserting the following code:
            </p>
            <div style="text-align: center; font-size: 24px; margin: 20px 0;">
                <strong style="background-color: #f0f0f0; padding: 10px; border-radius: 4px;">{confirmation_code}</strong>
            </div>
            <p style="font-size: 16px; line-height: 1.5;">
                Kind Regards,<br>
                <strong>MOM AI Team</strong>
            </p>
            <div style="text-align: center; margin-top: 20px;">
                <img src="https://i.ibb.co/LnWCxZF/MOMLogo-Small-No-Margins.png" alt="MOM AI Logo" style="width: 170px; height: 69px;">
            </div>
        </div>
    </body>
    </html>
    '''
    mail.send(msg)



# Function to send the confirmation email
def send_confirmation_email_change(mail, email, confirmation_code, from_email):
    msg = Message('MOM AI Restaurant Email Confirmation', recipients=[email], sender=("MOM AI Restaurant",from_email))
    # HTML content with bold and centered confirmation code
    msg.html = f'''
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px; color: #333;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
            <h2 style="color: #444;">MOM AI Restaurant</h2>
            <p style="font-size: 16px; line-height: 1.5;">
                You have requested account registration on MOM AI Restaurant.
            </p>
            <p style="font-size: 16px; line-height: 1.5;">
                Please confirm your email by inserting the following code:
            </p>
            <div style="text-align: center; font-size: 24px; margin: 20px 0;">
                <strong style="background-color: #f0f0f0; padding: 10px; border-radius: 4px;">{confirmation_code}</strong>
            </div>
            <p style="font-size: 16px; line-height: 1.5;">
                Kind Regards,<br>
                <strong>MOM AI Team</strong>
            </p>
            <div style="text-align: center; margin-top: 20px;">
                <img src="https://i.ibb.co/LnWCxZF/MOMLogo-Small-No-Margins.png" alt="MOM AI Logo" style="width: 170px; height: 69px;">
            </div>
        </div>
    </body>
    </html>
    '''
    mail.send(msg)





def send_confirmation_email_request_withdrawal(mail, email, restaurant_name, withdraw_amount, withdrawal_description, from_email):
    withdraw_amount = f'{withdraw_amount:.2f}'
    msg = Message('MOM AI Withdrawal Confirmation', recipients=[email], sender=("MOM AI Restaurant",from_email))
    msg_for_mom_ai =  Message('MOM AI Withdrawal Request', recipients=["contact@mom-ai-agency.site"], sender=from_email)
    msg_for_mom_ai.body = f'Hi, MOM AI\'s representative!\n\nThe restaurant {restaurant_name} - {email} has requested a withdrawal of {withdraw_amount} EUR.\n\nDescription is: \n\n{withdrawal_description}\n\nPlease, proceed with the withdrawal.'

    mail.send(msg_for_mom_ai)

    msg.body = f'Hi, {restaurant_name}\'s restaurant representative!\n\nThe request on withdrawal of {withdraw_amount} USD has been successfully submitted and is being processed.\n\nIn case we need any additional information, we will contact you.\n\nThank you for using MOM AI!'
    mail.send(msg)


def send_waitlist_email(mail, email, restaurant_name, from_email):
    msg = Message(f'{restaurant_name} is on MOM AI Waitlist!', recipients=[email], sender=("MOM AI Restaurant",from_email))
    msg_for_mom_ai =  Message('MOM AI Waitlist New Person', recipients=["contact@mom-ai-agency.site"], sender=from_email)
    msg_for_mom_ai.body = f'Hi, MOM AI\'s representative!\n\nThe restaurant {restaurant_name} - {email} has been added to the waitlist. Awesome!\n\nI love ya!'

    mail.send(msg_for_mom_ai)

    msg.html = f'''
    <html>
    <body>
        <p>Hi, {restaurant_name}\'s restaurant representative.
        <p>Your account has been successfully registered!</p>
        <p>Expect to hear from us in the middle of June to start innovating your customers\' ordering experience and increasing your profit margins!</p><br>
        <p>Kind Regards,<br>MOM AI Team</p>
        <img src="https://i.ibb.co/LnWCxZF/MOMLogo-Small-No-Margins.png" alt="MOM AI Logo" style="width: 170px; height: 69px;">
    </body>
    </html>
    '''
    mail.send(msg)

def send_confirmation_email_registered(mail, email, restaurant_name, from_email):
    msg = Message(f'{restaurant_name} is in MOM AI Family!', recipients=[email], sender=("MOM AI Restaurant",from_email))
    msg_for_mom_ai =  Message('MOM AI New Restaurant Registered', recipients=["contact@mom-ai-agency.site"], sender=from_email)
    msg_for_mom_ai.body = f'Hi, MOM AI\'s representative!\n\nThe restaurant {restaurant_name} - {email} has been registered. Awesome!\n\nI love ya!'

    mail.send(msg_for_mom_ai)

    msg.html = f'''
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px; color: #333;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
            <h2 style="color: #444;">Welcome to MOM AI Restaurant!</h2>
            <p style="font-size: 16px; line-height: 1.5;">
                Hi, {restaurant_name}'s restaurant representative.
            </p>
            <p style="font-size: 16px; line-height: 1.5;">
                Your account has been successfully registered!
            </p>
            <p style="font-size: 16px; line-height: 1.5;">
                Go to <a href="https://mom-ai-restaurant.pro/login" target="_blank" style="color: #1a73e8; text-decoration: none;">mom-ai-restaurant.pro</a> and start earning with AI.
            </p>
            <p style="font-size: 16px; line-height: 1.5;">
                Kind Regards,<br>
                <strong>MOM AI Team</strong>
            </p>
            <div style="text-align: center; margin-top: 20px;">
                <img src="https://i.ibb.co/LnWCxZF/MOMLogo-Small-No-Margins.png" alt="MOM AI Logo" style="width: 170px; height: 69px;">
            </div>
        </div>
    </body>
    </html>
    '''
    mail.send(msg)


def send_confirmation_email_quick_registered(mail, email, password, restaurant_name, from_email):
    msg = Message(f'{restaurant_name} is in MOM AI Family!', recipients=[email], sender=("MOM AI Restaurant",from_email))
    msg_for_mom_ai =  Message('MOM AI New Restaurant Registered', recipients=["contact@mom-ai-agency.site"], sender=from_email)
    msg_for_mom_ai.body = f'Hi, MOM AI\'s representative!\n\nThe restaurant {restaurant_name} - {email} has been registered. Awesome!\n\nI love ya!'

    mail.send(msg_for_mom_ai)

    msg.html = f'''
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px; color: #333;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
            <h2 style="color: #444;">Welcome to MOM AI Restaurant!</h2>
            <p style="font-size: 16px; line-height: 1.5;">
                Hi, {restaurant_name}'s restaurant representative.
            </p>
            <p style="font-size: 16px; line-height: 1.5;">
                Your account has been successfully registered!
            </p>
            <p style="font-size: 16px; line-height: 1.5;">
                Use this password to login now: <b>{password}</b>
            </p>
            <p style="font-size: 16px; line-height: 1.5;">
                Go to <a href="https://mom-ai-restaurant.pro/login" target="_blank" style="color: #1a73e8; text-decoration: none;">mom-ai-restaurant.pro</a> and start earning with AI.
            </p>
            <p style="font-size: 16px; line-height: 1.5;">
                Kind Regards,<br>
                <strong>MOM AI Team</strong>
            </p>
            <div style="text-align: center; margin-top: 20px;">
                <img src="https://i.ibb.co/LnWCxZF/MOMLogo-Small-No-Margins.png" alt="MOM AI Logo" style="width: 170px; height: 69px;">
            </div>
        </div>
    </body>
    </html>
    '''
    mail.send(msg)




def upload_image_to_imgbb(image_path, expiration=600):
    """
    Upload an image to imgbb.

    Parameters:
    api_key (str): Your imgbb API key.
    image_path (str): The file path to the image to be uploaded.
    expiration (int): The expiration time in seconds (default is 600 seconds).

    Returns:
    dict: The JSON response from the imgbb API.
    """

    api_key = os.environ.get("IMG_BB_API_KEY")
    # Define the URL
    url = "https://api.imgbb.com/1/upload"

    # Define the parameters
    params = {
        'expiration': expiration,
        'key': api_key
    }

    # Read the image file
    with open(image_path, "rb") as image_file:
        files = {
            'image': image_file
        }

        # Send the POST request
        response = requests.post(url, params=params, files=files)
    
    url = response["data"]["url"]

    return url

### Payments Section ###


# Just stuff for MOM token manipulations

"""
# Connect to the Polygon node (you can use Infura, Alchemy, or a local node)
polygon_url = "https://polygon-mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
web3 = Web3(Web3.HTTPProvider(polygon_url))

# Check connection
if web3.isConnected():
    print("Connected to Polygon node")
else:
    print("Failed to connect to Polygon node")

# Address and ABI of your deployed contract
contract_address = "0xYourContractAddressHere"
contract_abi = [
    # The ABI of your contract goes here
]

# Load the contract
contract = web3.eth.contract(address=contract_address, abi=contract_abi)



"""

