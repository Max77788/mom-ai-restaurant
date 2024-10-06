import os
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv
import requests

load_dotenv(find_dotenv())

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]

client = Client(account_sid, auth_token)

BLAND_TWILIO_KEY = os.environ.get("BLAND_TWILIO_KEY")
BLAND_AI_API_KEY = os.environ.get("BLAND_AI_API_KEY") 

BLAND_BASE_URL = "https://api.bland.ai/v1"

def get_available_phone_numbers(country_code):
    try:
        available_phone_numbers = client.available_phone_numbers(country_code).local.list()[0].phone_number
        return available_phone_numbers
    except Exception as e:
        print(f"Error while fetching {country_code} available phone numbers.")

def provision_twilio_number(phone_number):
    try:
        coolie = client.incoming_phone_numbers.create(phone_number=phone_number)
        return coolie
    except Exception as e:
        print(f"Error while provisioning {phone_number}. Error: {e}")

#phone_object = full_get_twilio_number("CA")
#print(phone_object)

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
  
    print(response.text)

    response_json = response.json()

    if response_json.get("status") == "success":
        return {"success":True, "phone_number":phone_number}
    else:
        return {"success":False, "phone_number":phone_number}


def full_get_insert_twilio_number(country_code):
    phone_number = get_available_phone_numbers(country_code)
    print(phone_number)
    response = provision_twilio_number(phone_number)
    print(response)
    response = insert_twilio_number(phone_number)
    if response.get("success"):
        # phone_object = {"phone_number": phone_number, "provision_sid": response.sid}
        return phone_number
    else:
        raise Exception("Failed to provision and insert phone number")


def get_country_pricing(country_code):
    try:
        countries = client.pricing.v1.phone_numbers.countries.list()
    except Exception as e:
        print(f"Error while fetching {country_code} pricing.")

    record = countries[0]
    for key, value in vars(record).items():
        print(f"{key}: {value}")