from flask import jsonify, session, request, url_for, flash, redirect
import pandas as pd
import openpyxl
import requests
from bs4 import BeautifulSoup
import ast
import re
import os
from flask_mail import Message
import uuid
from utils.pp_payment import SetExpressCheckout
import json
from openai import OpenAI
from time import sleep
from pymongo import MongoClient

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

mongodb_connection_string = os.environ.get("MONGODB_CONNECTION_URI")

# Connect to MongoDB
client_db = MongoClient(mongodb_connection_string)

# Specify the database name
db = client_db['MOM_AI_Restaurants']

# Specify the collection name
collection = db[os.environ.get("DB_VERSION")]

MOM_AI_JSON_LORD_ID = os.environ.get("MOM_AI_JSON_LORD_ID", "asst_YccYd0v0CbhweBvNMh0dJyJH")

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

CLIENT_OPENAI = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=53828)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def send_email(subject, body, to):
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)

    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    send_message = {'raw': raw_message}

    message = service.users().messages().send(userId="me", body=send_message).execute()
    print(f'Message Id: {message["id"]}. Message successfully sent to {to}!')
    return message



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

    if user:
        # Check the hashed password
        if user['password'] == password:
            return True
    return False

def insert_document(collection, name, email, password, website_url, assistant_id, menu_file_id, menu_vector_id, currency, html_menu, wallet_public_key_address, wallet_private_key, logo_id=None):
    """Insert a document into MongoDB that includes a name and two files."""
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    unique_azz_id = name+"_"+assistant_id[-4:]
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
            "web3_wallet_address": wallet_public_key_address,
            "web3_private_key": wallet_private_key,
            "balance": 3
            # "stripe_secret_test_key": stripe_secret_test_key
        }

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

**Completion:**

- Upon successful order confirmation, the action send_summary_to_json_azz is triggered.

**Additional Instructions:**

- It always uses the items provided in the attached menu.txt file for preparing the order summary.
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

And only after the user's confirmation does it trigger the function send_summary_to_json_azz.

- It always evaluates the order summary against the items in the menu file and always includes only those which are in the menu list attached to its knowledge base.
- NO ITEMS BEYOND THOSE WHICH ARE IN THE MENU FILE MUST BE OFFERED EVER!
                                              """, 
                                               model="gpt-4o",
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
        
        # Create a vector store called "Financial Statements"
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
        return assistant, "vector_is_not_yet", "menu_file_is_not_yet"


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







def get_assistants_response(user_message, thread_id, assistant_id, currency, menu_file_id, client_openai, list_of_all_items, unique_azz_id):
# Add the user's message to the thread

    client = client_openai

    user_message_enhanced = f"""
    Role: You are the best restaurant assistant who serves customers and register orders in the system
    
    Context: Identify users language. The customer asks you the question or writes the statement - your goal is to provide the response appropriately in the detected language
    facilitating order taking. To your knowledge base is attached the file menu_file.txt. The currency in which prices of the items are specified is {currency}.
    Recommend, suggest and anyhow use only and only the items specified in this file. Do not mention other dishes whatsoever! Do not include source in the final info.
    If the user confirms the order set up the status of the message 'requires_action'. Be sure to initiate action regardless of the language in which you communicate.
    Make sure that the item you suggest are from this list(also, included in the menu file attached to you):
    {list_of_all_items}
    Do not spit out all these items at once, refer to them only once parsed the attached menu to be sure that you are suggesting the right items.
    
    Task: Here is the current user's message, respond to it:
    {user_message}      
    (in the context of ongoing order taking process and attached to your knowledge base and to this message menu file)
    """
    
    user_message_is = f"""
    Hlutverk: Þú ert besti veitingastaðaþjónninn sem þjónar viðskiptavinum og skráir pantanir í kerfið.

    Samantekt: Viðskiptavinurinn spyr þig spurningu eða skrifar yfirlýsingu - markmið þitt er að svara viðeigandi til að auðvelda pöntunarferlið. Í þekkingargrunn þínum er skráin menu_file.txt. Gjaldmiðillinn sem verðið á réttunum er gefið upp í er {currency}. Mæltu með, stingdu upp á og notaðu einungis rétti sem eru tilgreindir í þessari skrá. Ekki nefna aðra rétti! Ekki innihalda uppruna í lokaupplýsingunum. Ef notandinn staðfestir pöntunina, settu stöðu skilaboðanna sem 'þarf aðgerðir'.

    Verkefni: Hér eru núverandi skilaboð notandans, svaraðu þeim:
    {user_message}
    (í samhengi við áframhaldandi pöntunarferli og meðfylgjandi skrá sem er menu_file)
"""
    
    #print(user_message_enhanced)
    #print(user_message_is)

    response = client.beta.threads.messages.create(thread_id=thread_id,
                                        role="user",
                                        content=user_message_enhanced,
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
            response = 'O-oh, little issues, type the other message now'
            return jsonify({"response": response}), 0
        sleep(1)  # Wait for a second before checking again
        if run_status.status == "requires_action":
            print("Action in progress...")
            
            # Retrieve and return the latest message from the Restaurant assistant
            messages_gpt = client.beta.threads.messages.list(thread_id=thread_id)

            print(f"Messages retrieved in action step {messages_gpt}") # debugging line


            #all_assistants_messages = []
            #all_users_messages = []

            #all_messages = []

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


            #all_messages.reverse()
            #all_users_messages.reverse()


            # Join the messages with two tabs
            # joined_messages_of_assistant = "\n\n".join(all_assistants_messages)

            # print(f"\nRetrieved Assistants messages with Summary from convo: {joined_messages_of_assistant}\n")
            print(f"\nRetrieved all messages with Summary from convo: {joined_messages_of_assistant}\n")

            

            summary_to_convert = f"""
            These are are all messages of the assistant from the chat with client. 
            From the following messages find the last one which summarizes agreed upon order and retrieve items stated in the final confirmed summary:
            {joined_messages_of_assistant}
            Ensure that the found items are part of this list:
            {list_of_all_items}
            """

            print(f"Summary to convert sent to MOM AI JSON: {summary_to_convert}") # debugging line

            thread_id_json = client.beta.threads.create().id
            print(f"JSON assistant thread {thread_id_json}")
              
            response = client.beta.threads.messages.create(thread_id=thread_id_json,                           
                                role="user",
                                content=summary_to_convert)

            # Run the MOM AI JSON LORD Assistant
            run_json = client.beta.threads.runs.create(thread_id=thread_id_json,
                                                    assistant_id=MOM_AI_JSON_LORD_ID)
            
            # Give some time to generate JSON object
            while True:
                run_status = client.beta.threads.runs.retrieve(thread_id=thread_id_json,
                                                            run_id=run_json.id)
                run_steps = client.beta.threads.runs.steps.list(
                thread_id=thread_id_json,
                run_id=run_json.id)
                
                print(f"Run status: {run_status.status}")
                if run_status.status == 'completed':
                    # Retrieve and return the latest message from the assistant
                    messages_gpt_json = client.beta.threads.messages.list(thread_id=thread_id_json)
                    
                    f"\n\nTokens used by JSON assistant: {run_status.usage.total_tokens}\n\n"
                    
                    total_tokens_used = run_status.usage.total_tokens

                    formatted_json_order = messages_gpt_json.data[0].content[0].text.value
                    print(f"\nFormatted JSON Order (Output from MOM AI JSON LORD): {formatted_json_order}\n")
                    
                    parsed_formatted_json_order = ast.literal_eval(formatted_json_order.strip())

                    print(f"Type of parsed response: {parsed_formatted_json_order}")
                    print(f"Keys of parsed response: {list(parsed_formatted_json_order.keys())}")

                    # Generate checkput link
                    #output = SetExpressCheckout(parsed_formatted_json_order["items"])

                    session["items_ordered"] = parsed_formatted_json_order["items"]
                    print(f"Setup the items ordered on assistant response! {parsed_formatted_json_order['items']}")

                    total = str(sum(float(float(item['amount'])*item['quantity']) for item in parsed_formatted_json_order["items"]))
                    session["total"] = total
                    print(f"Setup the total in session!")

                    

                    link_to_payment_buffer = url_for("payment_buffer", unique_azz_id=unique_azz_id)
                    print(link_to_payment_buffer)

                    # Wrap the output link in a clickable HTML element
                    clickable_link = f'<a href={link_to_payment_buffer} style="color: #c0c0c0;">Press here to proceed</a>'
                    response_cart = f"Order formed successfully. Please, follow this link to finish the purchase: {clickable_link}"

                    return response_cart, total_tokens_used
                if run_status.status == 'failed':
                    
                    print("Run of JSON assistant failed.")
                    # Access the last_error attribute
                    last_error = run_json.last_error if "last_error" in run else None

                    # Print the last_error if it exists
                    if last_error:
                        print("Last Error:", last_error)
                    else:
                        print("No errors reported for this run.")
                    
                    
                    print(f"\n\n Run steps: \n{run_steps}\n")
                    response = 'O-oh, little issues when running JSON assistant, type the other message now'
                    return jsonify({"response": response}), 0
                
    # Retrieve and return the latest message from the assistant
    messages_gpt = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages_gpt.data[0].content[0].text.value

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
            response = 'O-oh, little issues, type the other message now'
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
            clickable_link = f'<a href={link_to_payment_buffer} style="color: #e9e3e3;">Press here to proceed</a>'
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
    # Check if the DataFrame has exactly three columns
    if df.shape[1] != 3:
        raise InvalidMenuFormatError("Error in the menu - The input file must contain exactly three columns.")
    
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




def convert_xlsx_to_txt_and_menu_html(input_file_path, output_file_path, currency):
    # Load the XLSX file
    df = pd.read_excel(input_file_path, engine='openpyxl')

    df = df.fillna('No value provided')

    # Format the third column to two decimal places
    if df.shape[1] >= 3:  # Check if the DataFrame has at least three columns
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
            file.write(f"Item Name: {row[0]} - Item Ingredients: {row[1]} - Item Price in currency {currency}: {row[2]}\n")

    print(f"File successfully converted and saved as {output_file_path}")
    return output_file_path, html_menu

def generate_confirmation_code():
    return str(uuid.uuid4())[:7]

# Function to send the confirmation email
def send_confirmation_email(mail, email, confirmation_code, from_email):
    msg = Message('MOM AI Restaurant Email Confirmation', recipients=[email], sender=from_email)
    # HTML content with bold and centered confirmation code
    msg.html = f'''
    <html>
    <body>
        <p>You have requested account registration on MOM AI Restaturant Assistant.</p>
        <p>Please confirm your email by inserting the following code:</p>
        <div style="text-align: center; font-size: 20px">
            <strong>{confirmation_code}</strong>
        </div>
        <p>Kind Regards,<br>MOM AI Team</p>
        <img src="https://i.ibb.co/LnWCxZF/MOMLogo-Small-No-Margins.png" alt="MOM AI Logo" style="width: 170px; height: 69px;">
    </body>
    </html>
    '''
    mail.send(msg)

def send_confirmation_email_request_withdrawal(mail, email, restaurant_name, withdraw_amount, withdrawal_description, from_email):
    withdraw_amount = f'{withdraw_amount:.2f}'
    msg = Message('MOM AI Withdrawal Confirmation', recipients=[email], sender=from_email)
    msg_for_mom_ai =  Message('MOM AI Withdrawal Request', recipients=["contact@mom-ai-agency.site"], sender=from_email)
    msg_for_mom_ai.body = f'Hi, MOM AI\'s representative!\n\nThe restaurant {restaurant_name} - {email} has requested a withdrawal of {withdraw_amount} USD.\n\nDescription is: \n\n{withdrawal_description}\n\nPlease, proceed with the withdrawal.'

    mail.send(msg_for_mom_ai)

    msg.body = f'Hi, {restaurant_name}\'s restaurant representative!\n\nThe request on withdrawal of {withdraw_amount} USD has been successfully submitted and is being processed.\n\nIn case we need any additional information, we will contact you.\n\nThank you for using MOM AI!'
    mail.send(msg)


def send_waitlist_email(mail, email, restaurant_name, from_email):
    msg = Message(f'{restaurant_name} is on MOM AI Waitlist!', recipients=[email], sender=from_email)
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