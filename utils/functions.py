from flask import jsonify, session, request, url_for
import pandas as pd
import openpyxl
import requests
import ast
import os
from flask_mail import Message
import uuid
from utils.pp_payment import SetExpressCheckout
import json
from time import sleep
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

MOM_AI_JSON_LORD_ID = os.environ.get("MOM_AI_JSON_LORD_ID", "asst_YccYd0v0CbhweBvNMh0dJyJH")

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

def insert_document(collection, name, email, password, website_url, assistant_id, menu_file_id, menu_vector_id, wallet_public_key_address, wallet_private_key):
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
            "menu_file_id":menu_file_id,
            "menu_vector_id": menu_vector_id,
            "web3_wallet_address": wallet_public_key_address,
            "web3_private_key": wallet_private_key,
            "balance": 0
            # "stripe_secret_test_key": stripe_secret_test_key
        }

        # Insert document
        collection.insert_one(document)
        print("Restaurant instance inserted successfully.")
    
    except Exception as e:
        print(f"An error occurred: {e}")


def create_assistant(restaurant_name, menu_path, client):
    with open(str(menu_path), "rb") as menu:    
        menu_file = client.files.create(file=menu,
            purpose='assistants')
    menu_file_id = menu_file.id   

    #order_structure = """{"items":[{'name': 'Item Name', 'quantity': 2, 'amount':price of single item(e.g. 12.99, pull this info from attached menu file)}, 
    #{'name': 'Cake with Ice Cream', 'quantity': 3, 'amount':price of single item(e.g. 7.99, pull this info from attached menu file)}]}
    #"""
    
    assistant = client.beta.assistants.create(name=f"{restaurant_name} AI assistant", instructions=f"""
I am a specialized GPT designed to assist customers in selecting dishes from {restaurant_name}'s cuisine menu. My primary role is to help streamline the ordering process and provide a smooth and personalized dining experience.

The menu of {restaurant_name} is attached to your knowledge base. Please refer to the menu for accurate item names, prices, and descriptions.

Initial Interaction:

Observe the language used by the customer in their initial message and continue the conversation in that language to ensure effective communication.
Assist with the order immediately if the customer skips any preliminary greetings and proceeds directly to place an order.
Assistant Role Explanation (if asked):

Clearly describe your function as assisting customers in navigating {restaurant_name}'s menu, with the capability to automatically adapt and communicate in the customer's language.
Order Facilitation:

Offer personalized dish recommendations based on the customer’s preferences or suggest dishes based on your culinary expertise.
Present menu options and verify if the customer is ready to order or needs additional information.
Order Confirmation:

Recap the selected items before finalizing the order, ensuring the names (as listed in the menu), quantities, and prices are clear.
Checkout Process:

Confirm all order details with the customer before proceeding to the final confirmation.
Final Confirmation and Checkout:

Summarize the order in a clear and structured manner using the exact names from the menu file:
Example Order Summary:

Item Name - 12.99$, 1 item
Item Name - 8.99$, 3 items
Item Name - 9.99$, 2 items
Item Name - 8.99$, 1 item
Obtain the customer's confirmation on the order summary to ensure accuracy and satisfaction.

Once confirmed, trigger the function send_summary_to_json_azz which processes the details for the final checkout.

Completion:

Upon successful order confirmation, thank the customer and inform them with, "Congratulations, the order was taken!"
Additional Instructions:

Always use the items provided in the attached menu.txt file for preparing the order summary.
Ensure all items are accurately represented as listed in the menu and confirmed by the customer before proceeding to checkout.
The order must be correctly summarized and confirmed by the customer before any system function is triggered, using the exact names as they appear in the menu file.
System Integration:

Adapt to and use the customer's language for all communications without explicitly asking for their preference.
Consistently use the menu items from the attached file to ensure accuracy and consistency in order handling.
NO ITEMS BEYOND THOSE WHICH ARE IN THE MENU FILE MUST BE OFFERED EVER!
Before calling the function ALWAYS output the order summary like this:

Perfectly! Here is your order:

Item Name - $9.99, 2 servings
Item Name - $8.99, 1 serving
Item Name - $12.99, 2 servings

Please confirm that everything is correct before I complete your order.

And only after the user's confirmation do you trigger the function.

Always evaluate the order summary against the items in the menu file and always include only those which are in the menu list attached to your knowledge base.

NO ITEMS BEYOND THOSE WHICH ARE IN THE MENU FILE MUST BE OFFERED EVER!
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

    # Create a vector store caled "Financial Statements"
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







def get_assistants_response(user_message, thread_id, assistant_id, menu_file_id, client_openai):
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
                    output = SetExpressCheckout(parsed_formatted_json_order["items"], sandbox=True)

                    session['paypal_link'] = output
                    
                    link_to_payment_buffer = url_for("payment_buffer")
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
            clickable_link = f'<a href={link_to_payment_buffer} style="color: #c0c0c0;">Press here to proceed</a>'
            response_cart = f"Order formed successfully. Please, follow this link to finish the purchase: {clickable_link}"

            return response_cart, total_tokens_used
                
    # Retrieve and return the latest message from the assistant
    messages_gpt = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages_gpt.data[0].content[0].text.value

    return response, total_tokens_used






def send_telegram_notification(chat_id):
    bot_token = os.environ.get('TELEGRAM_TOKEN')  # Replace with your actual bot token
    chat_id = str(chat_id)      # Replace with your actual chat ID
    message = f"New order has been published! 🚀🚀🚀"
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=payload)
    print(response.json())




def convert_xlsx_to_txt_and_menu_items(input_file_path, output_file_path):
    # Load the XLSX file
    df = pd.read_excel(input_file_path, engine='openpyxl')
    
    # Retrieve the first column (assuming the first column has no header or has a header)
    #menu_items_list = df.iloc[:, 0].tolist()

    # Check if the DataFrame has at least two columns
    if df.shape[1] < 2:
        print("Error: The input file does not contain enough columns.")
        return
    
    # Open the output TXT file
    with open(output_file_path, 'w') as file:
        # Iterate through each row in the DataFrame
        for index, row in df.iterrows():
            # Write the first and second column values to the file
            file.write(f"Item Name: {row[0]} - Item Ingredients: {row[1]} - Item Price in US dollars: {row[2]}$\n")

    print(f"File successfully converted and saved as {output_file_path}")
    return output_file_path #menu_items_list

def generate_confirmation_code():
    return str(uuid.uuid4())

# Function to send the confirmation email
def send_confirmation_email(mail, email, confirmation_code, from_email):
    msg = Message('MOM AI Restaurant Email Confirmation', recipients=[email], sender=from_email)
    msg.body = f'Please confirm your email by inserting the following code:\n\n{confirmation_code}'
    mail.send(msg)

def send_confirmation_email_request_withdrawal(mail, email, restaurant_name, withdraw_amount, withdrawal_description, from_email):
    withdraw_amount = f'{withdraw_amount:.2f}'
    msg = Message('MOM AI Withdrawal Confirmation', recipients=[email], sender=from_email)
    msg_for_mom_ai =  Message('MOM AI Withdrawal Request', recipients=["contact@mom-ai-agency.site"], sender=from_email)
    msg_for_mom_ai.body = f'Hi, MOM AI\'s representative!\n\nThe restaurant {restaurant_name} - {email} has requested a withdrawal of {withdraw_amount} USD.\n\nDescription is: \n\n{withdrawal_description}\n\nPlease, proceed with the withdrawal.'

    mail.send(msg_for_mom_ai)

    msg.body = f'Hi, {restaurant_name}\'s restaurant representative!\n\nThe request on withdrawal of {withdraw_amount} USD has been successfully submitted and is being processed.\n\nIn case we need any additional information, we will contact you.\n\nThank you for using MOM AI!'
    mail.send(msg)


### Payments Section ###