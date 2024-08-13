import requests
import os
from dotenv import load_dotenv, find_dotenv
from flask import jsonify
load_dotenv(find_dotenv())

BLAND_AI_API_KEY = os.environ.get("BLAND_AI_API_KEY") 

BLAND_BASE_URL = "https://api.bland.ai/v1"

PATHWAY_NODES = f"""
               
"""

def send_the_call_on_number_demo(where_to_call, restaurant_name, language, timezone):
    url = BLAND_BASE_URL+"/calls"
    
    payload = {
    "phone_number": where_to_call,
    "task": f"""
              You are Maya, a customer service agent at {restaurant_name} restaurant 
              calling the manager of {restaurant_name} to introduce yourself 
              as an AI-empowered voice agent capable of taking orders,
              responding to customer inquiries, reserve tables and even handles small talk
              with little jokes. At the end of the call tell to continue on MOM AI Restaurant 
              platform to set {restaurant_name}'s voice agent completely and get their own 
              dedicated AI-employee.
              """,
    "pathway_id": "e9d3bda5-2c57-484f-8443-bd0ed3e26435",
    #"start_node_id": "<string>",
    "voice": "maya",
    #"first_sentence": f"""
                        #Hi, my name is Maya - 
                        #I am a customer service agent at 
                        #{restaurant_name} restaurant.
                        #How may I help you?
                        #""",
    #"wait_for_greeting": True,
    "block_interruptions": True,
    "interruption_threshold": 100,
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
    "max_duration": 7,
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
    url = f"https://api.bland.ai/v1/convo_pathway/e9d3bda5-2c57-484f-8443-bd0ed3e26435"
    headers = {
        "authorization": BLAND_AI_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.request("GET", url, headers=headers)

    # print(response.text)

    return response.json()

def create_the_suitable_pathway(restaurant_name, store_location, opening_hours, timezone, restaurant_menu):
    # Define the replacement values
    replacements = {
        "{{ restaurant_name }}": restaurant_name,
        "{{restaurant_name}}": restaurant_name,
        "{{store_location}}": store_location,
        "{{opening_hours}}": opening_hours,
        "{{timezone}}": timezone,
        "{{restaurant_menu}}": restaurant_menu
    }

    # Open the file and read its contents into a string
    with open("bland/pathway_nodes.txt", 'r') as file:
        file_contents = file.read()
        
    # Replace placeholders with actual values
    for placeholder, actual_value in replacements.items():
        file_contents = file_contents.replace(placeholder, actual_value)

    with open(f"bland/pathways_{restaurant_name}", "w") as file:
        file.write(file_contents)
    print("Everything is transformed.")

    return None
    
    