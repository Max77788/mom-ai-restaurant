import requests
import json
import os
import hyperwallet
import secrets
import string
from flask import session
import uuid
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# Hyperwallet API credentials
username = os.environ.get('HYPERWALLET_USERNAME')
password = os.environ.get('HYPERWALLET_PASSWORD')
program_token = os.environ.get('HYPERWALLET_PROGRAM_TOKEN')

api = hyperwallet.Api(
    username,
    password,
    program_token
)

# Hyperwallet API URLs
base_url = 'https://sandbox.hyperwallet.com'  # Change to live URL for live transactions


def generate_random_string(length=8):
    # Define the character set: uppercase, lowercase, and digits
    characters = string.ascii_letters + string.digits
    # Generate a random string
    random_string = ''.join(secrets.choice(characters) for i in range(length))
    return random_string

def generate_random_number_string(length=8):
    # Define the character set: digits
    characters = string.digits
    # Generate a random string of numbers
    random_number_string = ''.join(secrets.choice(characters) for _ in range(length))
    return random_number_string

# Function to create a user
def create_user(first_name, last_name, email, addressLine, city, stateProvince, country, postalCode, date_of_birth="1980-01-01", api=api):
    #url = f"{base_url}/rest/v4/users"
    
    unique_aydi = first_name+"_"+last_name+"_"+email
    payload = {
  "clientUserId": unique_aydi,
  "profileType": "BUSINESS",
  "firstName": first_name,
  "lastName": last_name,
  "dateOfBirth": date_of_birth,
  "email": email,
  "addressLine1": addressLine,
  "city": city,
  "stateProvince": stateProvince,
  "country": country,
  "postalCode": postalCode,
  "programToken": program_token,
  "businessName": session.get('restaurant_name'),
}

    response = api.createUser(payload)
    return response.json()

# Function to create a bank account
def create_bank_account(user_token, swift_id, iban_id, address_line, city, api=api):
    
    data = {
  "profileType": "BUSINESS",
  "transferMethodCountry": "IS",
  "transferMethodCurrency": "USD",
  "type": "WIRE_ACCOUNT",
  "bankId": swift_id,
  "bankAccountId": iban_id,
  "businessName": session.get('restaurant_name'),
  "country": "IS",
  "addressLine1": address_line,
  "city": city,
  "bankAccountRelationship": "OWN_COMPANY"
}
    response = api.createBankAccount(user_token, data)

    return response.json()

# Function to make a payment
def make_payment(amount_usd, user_token, api=api):
    
    # Generate a random string of length 8
    payment_id = generate_random_string(8)
    
    data = {
    "amount": amount_usd,
    "clientPaymentId": payment_id,
    "currency": "USD",
    "destinationToken": user_token,
    "programToken": program_token,
    "purpose": "OTHER"
    }
    response = api.createPayment(data)
    
    return response.json()

def create_transfer(user_token, bank_user_token, amount_usd, api=api):
    unique_num_id = generate_random_number_string(15)
    
    note = f"withdrawal of {amount_usd} to {session.get('restaurant_name')}'s Bank Account"

    memo = "MOM AI Loves You!"
    
    data = {
    "clientTransferId": unique_num_id,
    "destinationAmount": str(amount_usd),
    "destinationCurrency": "USD",
    "notes": note,
    "memo": memo,
    "sourceToken": user_token,
    "destinationToken": bank_user_token
    }
    response = api.createTransfer(data)

    return response.json()










# Main function to execute the payout
def main():
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@example.com"
    amount = "10.00"

    user_response = create_user(first_name, last_name, email)
    user_token = user_response.get('token')

    bank_account_details = {
        "transferMethodCountry": "US",
        "transferMethodCurrency": "USD",
        "type": "BANK_ACCOUNT",
        "bankAccountPurpose": "CHECKING",
        "branchId": "123456789",  # Bank routing number
        "bankAccountId": "987654321",  # Bank account number
        "bankAccountHolderName": "John Doe"
    }

    bank_account_response = create_bank_account(user_token, bank_account_details)
    payment_response = make_payment(user_token, amount)

    print(json.dumps(payment_response, indent=4))

if __name__ == "__main__":
    main()
