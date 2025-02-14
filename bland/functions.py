import requests
import os
from deep_translator import GoogleTranslator
import json
from dotenv import load_dotenv, find_dotenv
from flask import jsonify
load_dotenv(find_dotenv())
import os
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv
from bland.twilio_stuff import full_get_insert_twilio_number

load_dotenv(find_dotenv())

MOM_AI_BLAND_RESTAURANT_GENIE_ID = "82c1a525-0de5-4436-ae12-c68b2be884c0"

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]

client = Client(account_sid, auth_token)


BLAND_TWILIO_KEY = os.environ.get("BLAND_TWILIO_KEY")
BLAND_AI_API_KEY = os.environ.get("BLAND_AI_API_KEY") 

BLAND_BASE_URL = "https://api.bland.ai/v1"

language_codes = {
    "en": "English",
    "en-US": "English (US)",
    "en-GB": "English (UK)",
    "en-AU": "English (Australia)",
    "en-NZ": "English (New Zealand)",
    "en-IN": "English (India)",
    "zh": "Chinese (Mandarin, Simplified)",
    "zh-CN": "Chinese (Mandarin, Simplified, China)",
    "zh-Hans": "Chinese (Mandarin, Simplified, Hans)",
    "zh-TW": "Chinese (Mandarin, Traditional)",
    "zh-Hant": "Chinese (Mandarin, Traditional, Hant)",
    "es": "Spanish",
    "es-419": "Spanish (Latin America)",
    "fr": "French",
    "fr-CA": "French (Canada)",
    "de": "German",
    "el": "Greek",
    "hi": "Hindi",
    "hi-Latn": "Hindi (Latin script)",
    "ja": "Japanese",
    "ko": "Korean",
    "ko-KR": "Korean (Korea)",
    "pt": "Portuguese",
    "pt-BR": "Portuguese (Brazil)",
    "it": "Italian",
    "nl": "Dutch",
    "pl": "Polish",
    "ru": "Russian",
    "sv": "Swedish",
    "sv-SE": "Swedish (Sweden)",
    "da": "Danish",
    "da-DK": "Danish (Denmark)",
    "fi": "Finnish",
    "id": "Indonesian",
    "ms": "Malay",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "bg": "Bulgarian",
    "cs": "Czech",
    "ro": "Romanian",
    "sk": "Slovak"
}



def get_available_phone_numbers(country_code):
    try:
        available_phone_numbers = client.available_phone_numbers(country_code).toll_free.list()[0].phone_number
        return available_phone_numbers
    except Exception as e:
        print(f"Error while fetching {country_code} available phone numbers.")

def provision_twilio_number(phone_number):
    try:
        coolie = client.incoming_phone_numbers.create(phone_number=phone_number)
        return coolie
    except Exception as e:
        print(f"Error while provisioning {phone_number}. Error: {e}")

def full_get_twilio_number(country_code):
    phone_number = get_available_phone_numbers(country_code)
    print(phone_number)
    response = provision_twilio_number(phone_number)
    print(response)
    phone_object = {"phone_number": phone_number, "provision_sid": response.sid}
    return phone_object

def get_twilio_number(sid_thing):
    incoming_phone_number = client.incoming_phone_numbers(
        sid_thing
    ).fetch()
    return incoming_phone_number



def insert_twilio_number(phone_number):
    url = BLAND_BASE_URL+"/inbound/insert"

    payload = {"numbers": [phone_number]}
    headers = {
        "authorization": BLAND_AI_API_KEY,
        "encrypted_key": BLAND_TWILIO_KEY,
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    response_json = response.json()

    if response_json["status"] == "success":
        return {"success":True, "phone_number":phone_number}
    else:
        return {"success":False, "phone_number":phone_number}




def send_the_call_on_number_demo(where_to_call, restaurant_name, language, store_location, opening_hours, timezone):
    url = BLAND_BASE_URL+"/calls"
    
    payload = {
    "phone_number": where_to_call,
    "task": f"""
              Speak in this language - {language_codes[language]}.
              You are Maya, a customer service agent at {restaurant_name} restaurant 
              calling the manager of {restaurant_name} to introduce yourself 
              as an AI-empowered voice agent capable of taking orders,
              responding to customer inquiries, reserve tables and even handles small talk
              with little jokes. Then tell the user to create a fully working 
              AI-voice-agent by simply pressing the button beneath the section where he triggered this demo call.
              Warn the user that the call is restarained to 3 minutes and if he wants you can have a generic
              chit-chat for the rest of the call's time and then the user can create {restaurant_name}'s AI-voice-agent 
              by simply pressing the button on the page he is currently on.
              """,
    #"pathway_id": "e9d3bda5-2c57-484f-8443-bd0ed3e26435",
    #"start_node_id": "<string>",
    "voice": "alexa",
    #"first_sentence": f"""
                        #Hi, my name is Maya - 
                        #I am a customer service agent at 
                        #{restaurant_name} restaurant.
                        #How may I help you?
                        #""",
    #"wait_for_greeting": True,
    "block_interruptions": True,
    "interruption_threshold": 70,
    "model": "enhanced",
    "temperature": 0.5,
    #"keywords": ["<string>"],
    #"pronunciation_guide": [{}],
    #"transfer_phone_number": "<string>",
    #"transfer_list": {},
    "language": language,
    #"calendly": {},
    #"timezone": "<string>",
    "request_data": {
        "restaurant_name":restaurant_name,
        "timezone":timezone,
        "store_location":store_location,
        "opening_hours":opening_hours,
    },
    #"tools": [{}],
    #"dynamic_data": [{"dynamic_data[i].response_data": [{}]}],
    #"start_time": "<string>",
    #"voicemail_message": "<string>",
    #"voicemail_action": {},
    #"retry": {},
    "max_duration": 3,
    #"record": True,
    #"from": "<string>",
    #"webhook": "<string>",
    #"metadata": {},
    #"summary_prompt": "<string>",
    #"analysis_prompt": "<string>",
    #"analysis_schema": {},
    #"answered_by_enabled": True
    }
    headers = {
        "authorization": BLAND_AI_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.text)
    if response.json().get("status") == "success":
        return True
    else:
        return False
    
def get_conversational_pathway_data():
    url = BLAND_BASE_URL + f"/convo_pathway/{MOM_AI_BLAND_RESTAURANT_GENIE_ID}"
    headers = {
        "authorization": BLAND_AI_API_KEY
    }

    response = requests.request("GET", url, headers=headers)

    # print(response.text)

    response_json = response.json()

    print(f"Template stuff: {response_json}")

    # with open("bland/pathway_nodes.txt", "w") as file:
        # json.dump(response_json, file, ensure_ascii=False, indent=4)

    return response_json

def create_the_suitable_pathway_script(unique_azz_id, restaurant_language_code="en-US"):
    restaurant_language = language_codes[restaurant_language_code]
    
    # Define the replacement values
    replacements = {
        "{{ unique_azz_id }}": unique_azz_id,
        "{{ restaurant_language }}": restaurant_language
    }

    file_contents = get_conversational_pathway_data()

    # Open the file and load its JSON content into a dictionary
    # with open("bland/pathway_nodes.txt", 'r') as file:
        # file_contents = json.load(file)
        
    # Replace placeholders in all string values within the JSON structure
    def replace_placeholders(obj):
        if isinstance(obj, dict):
            return {k: replace_placeholders(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_placeholders(i) for i in obj]
        elif isinstance(obj, str):
            for placeholder, actual_value in replacements.items():
                obj = obj.replace(placeholder, actual_value)
            return obj
        else:
            return obj

    # Apply replacements
    updated_contents = replace_placeholders(file_contents)

    # Write the modified JSON content to a new file with double-quoted keys
    # with open(f"bland/pathways/pathways_{unique_azz_id}.txt", "w") as file:
        # json.dump(updated_contents, file, ensure_ascii=False, indent=4, separators=(',', ': '))

    # print("Everything is transformed.")

    return updated_contents

    
def create_fully_new_pathway(restaurant_name):
    url = BLAND_BASE_URL+"/convo_pathway/create"

    payload = {
        "name": f"{restaurant_name}'s Voice Agent",
        "description": f"Designed to take orders and loyally serve customers of {restaurant_name} restaurant"
    }
    headers = {
        "authorization": f"{BLAND_AI_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    # print(response.text)

    return response.json()["pathway_id"]




def insert_the_nodes_and_edges_in_new_pathway(pathway_id, new_script):
    url = BLAND_BASE_URL+ f"/convo_pathway/{pathway_id}"

    headers = {
        "authorization": BLAND_AI_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=new_script, headers=headers)

    # print(response.text)

    response_json = response.json()

    if response_json["status"] == "success":
        print("Updated pathway successfully!")
        return True
    else:
        print("Something went wrong during pathway updating!")
        return False


def pathway_serving_a_to_z_initial(restaurant_name, store_location, opening_hours, timezone, restaurant_menu, res_currency, unique_azz_id):
    
    new_script = create_the_suitable_pathway_script(unique_azz_id)

    pathway_id = create_fully_new_pathway(restaurant_name)
    
    new_script["name"] = f"{restaurant_name}'s Voice Agent",
    new_script["description"] = f"Designed to take orders and loyally serve customers of {restaurant_name} restaurant"

    success = insert_the_nodes_and_edges_in_new_pathway(pathway_id, new_script)

    #print("Pathway ID at the end: ", pathway_id)
    
    if success:
        return {"success":True, "pathway_id": pathway_id}
    else:
        return {"success":False, "pathway_id": None}

def pathway_proper_update(restaurant_name, store_location, opening_hours, timezone, restaurant_menu, unique_azz_id, pathway_id, language_code):
    new_script = create_the_suitable_pathway_script(unique_azz_id, language_code)

    new_script["name"] = '{}\'s Voice Agent'.format(restaurant_name),
    new_script["description"] = f"Designed to take orders and loyally serve customers of {restaurant_name} restaurant"

    success = insert_the_nodes_and_edges_in_new_pathway(pathway_id, new_script)

    if success:
        return True
    else:
        return False

def purchase_phone_number():
    url = BLAND_BASE_URL + "/inbound/purchase"

    payload = {
        "country_code": "CA",
        "webhook": "https://mom-ai-restaurant.pro/charge-for-call"
    }

    headers = {
        "authorization": BLAND_AI_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    print("From purchase phone number route")
    print(response.json())
    
    return response.json()["phone_number"]


def update_phone_number(phone_number, language, timezone, pathway_id):
    url = BLAND_BASE_URL + f"/inbound/{phone_number}"

    payload = {
        "pathway_id":pathway_id,
        "voice": "e1289219-0ea2-4f22-a994-c542c2a48a0f",
        "language":language,
        "timezone":timezone,
        "interruption_threshold":70,
        "webhook": "https://mom-ai-restaurant.pro/charge-for-call"
    }

    headers = {
    "authorization": BLAND_AI_API_KEY,
    "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    response_json = response.json()

    print(response.text)

    if response_json["status"] == "success":
        return True
    else:
        return False
    
def get_data_for_pathway_change(restaurant):   
    restaurant_menu_tuples = restaurant.get("html_menu_tuples")

    menu_string = ""

    for item in restaurant_menu_tuples:
        item_text = f"Name: {item['Item Name']}\nIngredients: {item['Item Description']}\nPrice: {item['Item Price (EUR)']} EUR\n\n\n"
        menu_string += item_text
    
    restaurant_name = restaurant.get("name")
    store_location = restaurant.get("location_name")
    timezone = restaurant.get("timezone")
    res_currency = restaurant.get("res_currency")

    restaurant_menu = menu_string
    
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
    
    return restaurant_name, store_location, opening_hours_string, timezone, restaurant_menu, res_currency
    
def update_phone_number_non_english(phone_number, restaurant_name, restaurant_menu, working_hours, store_location, language, timezone):
    url = BLAND_BASE_URL + f"/inbound/{phone_number}"
    
    NON_ENGLISH_INSTRUCTIONS_BASE = f"""
    You the customer service agent at '{restaurant_name}' restaurant.
    You are able to provide the customer with the information on the menu, location and working hours of the restaurant.
    You do not take orders.
    There are menu, working schedule, timezone and location of the restaurant:
     """
    
    # translator = GoogleTranslator(source="auto", target=language[:2]) 
    # translated_instruction = translator.translate(NON_ENGLISH_INSTRUCTIONS_BASE)
    
    translated_instruction += f"""
    -------------------------
    Restaurant Menu:
    {restaurant_menu}
    -------------------------
    Working Schedule:
    {working_hours}
    -------------------------
    Timezone:
    {timezone}
    -------------------------
    Store Location:
    {store_location}
    """

    NON_ENGLISH_INSTRUCTIONS_TRANSLATED = translated_instruction

    payload = {
        "prompt": NON_ENGLISH_INSTRUCTIONS_TRANSLATED,
        "voice": "e1289219-0ea2-4f22-a994-c542c2a48a0f",
        "language":language,
        "timezone":timezone,
        "interruption_threshold":70,
        "webhook": "https://mom-ai-restaurant.pro/charge-for-call"
    }

    headers = {
    "authorization": BLAND_AI_API_KEY,
    "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    response_json = response.json()

    print(response.text)

    if response_json["status"] == "success":
        return True
    else:
        return False


def get_call_length_and_phone_number(call_id):
    url = f"https://api.bland.ai/v1/calls/{call_id}"

    headers = {"authorization": BLAND_AI_API_KEY}

    response = requests.request("GET", url, headers=headers)

    response_json = response.json()

    call_length = response_json["call_length"]
    restaurant_phone_number = response_json["to"]

    return call_length, restaurant_phone_number


def add_pathway_to_phone(phone_number, pathway_id, language, timezone):
    url = BLAND_BASE_URL + f"/inbound/{phone_number}"

    payload = {
        "voice": "e1289219-0ea2-4f22-a994-c542c2a48a0f",
        "pathway_id":pathway_id,
        "language":language,
        "timezone": timezone,
        "interruption_threshold":70,
        "webhook": "https://mom-ai-restaurant.pro/charge-for-call"
    }

    headers = {
    "authorization": BLAND_AI_API_KEY,
    "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    response_json = response.json()

    print(response.text)

    if response_json["status"] == "success":
        return True
    else:
        return False


def buy_and_update_phone(pathway_id, language, timezone):
    # phone_number = purchase_phone_number()
    try:
        phone_number = full_get_insert_twilio_number("US")
        update_phone_number(phone_number, language, timezone, pathway_id)
    except Exception as e:
        print(str(e))
        raise (e)

    success = add_pathway_to_phone(phone_number, pathway_id, language, timezone)

    return {"success":success, "phone_number":phone_number}