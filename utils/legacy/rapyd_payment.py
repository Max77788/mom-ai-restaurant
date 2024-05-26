from pprint import pprint
from flask import redirect
import time
from utils.rapyd_utilities import make_request
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())  

rapyd_api_key = os.environ.get('RAPYD_SANDBOX_SECRET_KEY')

payment_method_types = [
        "us_debit_visa_card",
        "us_debit_mastercard_card"
    ]

# Create a checkout page
def create_checkout_page(items, expiration_ts=time.time() + 604800):
    
    amount = sum(item['amount'] * item['quantity'] for item in items)

    checkout_page = {
    "amount": amount,
    "complete_payment_url": "https://ai-restaurant-mom.online/trigger_binance_withdrawal",
    "cart_items": items,
    "country": "US",
    "currency": "usd",
    #"customer": customer_token,
    "error_payment_url": "https://ai-restaurant-mom.online/error_payment",
    "merchant_reference_id": "biryani",
    "language": "en",
    "metadata": {
        "merchant_defined": True
    },
    "expiration": expiration_ts,
    "payment_method_types_include": payment_method_types
}
    result = make_request(method='post', path='/v1/checkout', body=checkout_page)

    checkout_page_url = result['data']['redirect_url']

    return checkout_page_url
