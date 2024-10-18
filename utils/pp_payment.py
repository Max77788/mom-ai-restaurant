from uuid import uuid4
from paypalrestsdk import Payment, WebProfile
from paypalrestsdk import Api as PaypalAPI
import uuid 
import json
import requests
import logging
import os
from flask import url_for, session
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID") if os.environ.get("PAYPAL_SANDBOX") == "True" else os.environ.get("PAYPAL_LIVE_CLIENT_ID")
SECRET_KEY = os.environ.get("PAYPAL_SECRET_KEY") if os.environ.get("PAYPAL_SANDBOX") == "True" else os.environ.get("PAYPAL_LIVE_SECRET_KEY")

SANDBOX = True if os.environ.get("PAYPAL_SANDBOX") == "True" else False

# print(f'os.environ.get("PAYPAL_SANDBOX") is {os.environ.get("PAYPAL_SANDBOX")}')

BASE_URL = "https://api.sandbox.paypal.com" if SANDBOX else "https://api.paypal.com"
# print(f"BASE_URL sandbox - {SANDBOX}")

api = PaypalAPI({
            'mode': 'sandbox' if SANDBOX else 'live',
            'client_id': CLIENT_ID,
            'client_secret': SECRET_KEY}
            )

def transform_items(input_data):
    transformed_items = []
     
    currency=session.get("res_currency") 
    currency="EUR"

    for item in input_data:
        # Calculate the total price as quantity * amount, but amount should be per item already
        price_per_item = item['amount']  # The price is assumed to be given per single item

        # Create a new dictionary with the desired structure
        new_item = {
            'name': item['name'],
            'price': f'{price_per_item:.2f}',  # Format the price to two decimal places
            'currency': currency,
            'quantity': item['quantity']
        }
        transformed_items.append(new_item)

    return transformed_items



def SetExpressCheckout(items, profile=None, sandbox=SANDBOX, client_id=CLIENT_ID, secret_key=SECRET_KEY):

    url_success = f"{url_for('success_payment', _external=True)}"
    url_cancel = f"{url_for('cancel_payment', _external=True)}"

    if sandbox:
        print("Sandbox mode is enabled")

    items = transform_items(items)
    currency_of_order = items[0]["currency"]

    currency_of_order = "EUR"

    print(items)

    total = str(sum(float(float(item['price'])*item['quantity']) for item in items))

    print(total)

    session['items_ordered'] = items  # Store items in the session for later use
    session['total'] = total  

    print("Session items ordered: ", session['items_ordered'])
    #print("Session 99% total and total: ", session['total'], total)

    data= {
                 'intent': 'sale',
                 'payer': {
                     'payment_method': 'paypal',
                      },
                  'note_to_payer': 'A note',
                  'redirect_urls': {
                      'return_url': url_success,
                      'cancel_url': url_cancel,
                      },
                  'transactions': [{
                      'notify_url': 'https://www.shop.com/paypal_notify.py',
                      'item_list': {
                          'items': items,
                          },
                      'amount': {
                          'total': total,
                          'currency': currency_of_order,
                          },
                      'description': 'Description',
                      'payment_options': {
                          'allowed_payment_method': 'INSTANT_FUNDING_SOURCE',
                          },
                      }],
                  }
    
    api = PaypalAPI({
            'mode': 'sandbox' if sandbox else 'live',
            'client_id': client_id,
            'client_secret': secret_key}
            )
    if profile:
        profile['name'] = uuid4().hex
        profile['temporary'] = True
        webprofile = WebProfile(profile, api=api)
        if not webprofile.create():
            raise Exception(webprofile.error)
        data['experience_profile_id'] = webprofile.id

    payment = Payment(data, api=api)

    print("Payment Created!")
    
    if not payment.create():
        raise Exception(payment.error)
    
    print(payment.links)
    
    for link in payment.links:
        if link.method == 'REDIRECT':
            redirect_url = link.href
            redirect_url += '&useraction=continue' #'&useraction=commit'
            break        
    session['paypal_link'] = redirect_url
    
    return redirect_url


def createPayment(items, profile=None, sandbox=SANDBOX, client_id=CLIENT_ID, secret_key=SECRET_KEY):

    url_success = f"{url_for('success_payment', _external=True)}"
    url_cancel = f"{url_for('cancel_payment', _external=True)}"

    if sandbox:
        print("Sandbox mode is enabled")

    items = transform_items(items)
    currency_of_order = items[0]["currency"]

    currency_of_order = "EUR"

    #print(items)

    total = str(sum(float(float(item['price'])*item['quantity']) for item in items))

    print(total)

    session['items_ordered_pp'] = items  # Store items in the session for later use
    session['total'] = total  

    print("Session items ordered: ", session['items_ordered_pp'])
    #print("Session 99% total and total: ", session['total'], total)

    data= {
                 'intent': 'sale',
                 'payer': {
                     'payment_method': 'paypal',
                      },
                  'note_to_payer': 'A note',
                  'redirect_urls': {
                      'return_url': url_success,
                      'cancel_url': url_cancel,
                      },
                  'transactions': [{
                      'notify_url': 'https://www.shop.com/paypal_notify.py',
                      'item_list': {
                          'items': items,
                          },
                      'amount': {
                          'total': total,
                          'currency': currency_of_order,
                          },
                      'description': 'Description',
                      'payment_options': {
                          'allowed_payment_method': 'INSTANT_FUNDING_SOURCE',
                          },
                      }],
                  }
    
    api = PaypalAPI({
            'mode': 'sandbox' if sandbox else 'live',
            'client_id': client_id,
            'client_secret': secret_key}
            )
    if profile:
        profile['name'] = uuid4().hex
        profile['temporary'] = True
        webprofile = WebProfile(profile, api=api)
        if not webprofile.create():
            raise Exception(webprofile.error)
        data['experience_profile_id'] = webprofile.id

    payment = Payment(data, api=api)

    print("Payment Created!")
    
    if not payment.create():
        raise Exception(payment.error)
    
    return payment


def executePayment(paymentID:str, payerID:str):
    # ID of the payment. This ID is provided when creating payment.
    payment = Payment.find(paymentID, api=api)

    # PayerID is required to approve the payment.
    if payment.execute({"payer_id": payerID}):  # return True or False
        print("Payment[%s] execute successfully" % (payment.id))
        return True
    else:
        print(payment.error)
        return False
    

def get_access_token(client_id=CLIENT_ID, secret_key=SECRET_KEY):
    url = f"{BASE_URL}/v1/oauth2/token"
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US"
    }
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(url, headers=headers, data=data, auth=(client_id, secret_key))
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        logging.error(f"Failed to get access token: {response.json()}")
        return None

def get_subscription_status(subscription_id, access_token=get_access_token()):
    url = f"{BASE_URL}/v1/billing/subscriptions/{subscription_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        subscription = response.json()
        return subscription.get('status', 'Unknown status')
    elif response.status_code == 404:
        logging.error(f"Subscription not found: {response.json()}")
        return "Subscription not found"
    else:
        logging.error(f"Error retrieving subscription status: {response.json()}")
        return "Error retrieving subscription status"
    
def createOrder(total_to_pay, unique_azz_id=None):
    
    access_token=get_access_token()

    session["access_token"] = access_token

    reference_id = str(uuid.uuid4())
    session["request_id"] = reference_id

    headers = {
        'Content-Type': 'application/json',
        'PayPal-Request-Id': f'{reference_id}',
        'Authorization': f'Bearer {access_token}',
    }
 
    currency_code = session.get("res_currency", "EUR")
    currency_code = "EUR"
    
    session_total = float(session.get('total', 10))
    
    '''
    if addFees:
        print("Entered addFees loop")
        print("Session total ", session_total)
        amount = f"{session_total+0.45+(0.049*session_total):.2f}"
        print("Amount formed ", amount)
    else:
        amount = f"{session_total:.2f}"
    '''
    
    restaurant_name = session.get("restaurant_name", "restaurant_name_place") 
    print(f"Data on /createOrder:\n\n{currency_code, reference_id, total_to_pay, restaurant_name}")

    unique_azz_id = session.get('unique_azz_id', unique_azz_id)
    
    data = f'''
{{
    "intent": "CAPTURE",
    "purchase_units": [
        {{
            "reference_id": "{reference_id}",
            "amount": {{
                "currency_code": "{currency_code}",
                "value": "{total_to_pay}"
            }}
        }}
    ],
    "payment_source": {{
        "paypal": {{
            "experience_context": {{
                "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                "brand_name": "MOM AI - {restaurant_name.replace("_", " ")}",
                "locale": "en-US",
                "landing_page": "LOGIN",
                "user_action": "PAY_NOW",
                "return_url": "https://example.com/returnUrl",
                "cancel_url": "https://example.com/cancelUrl"
            }}
        }}
    }}
}}
'''

    response = requests.post(f'{BASE_URL}/v2/checkout/orders', headers=headers, data=data)

    if response.status_code in [201,200]:
        print("Order created successfully.")
        print(f"Type of order is {type(response)}")
    else:
        print(f"Failed to create order: {response.status_code} {response.text}")

    return response

def captureOrder(order_id):
    access_token = session.get("access_token")
    request_id = str(uuid.uuid4())

    headers = {
    'Content-Type': 'application/json',
    'PayPal-Request-Id': request_id,
    'Authorization': f'Bearer {access_token}',
}
    print(f'On capture order: Order ID {order_id}, Headers: {headers}')

    response = requests.post(f'{BASE_URL}/v2/checkout/orders/{order_id}/capture', headers=headers)
    return response
