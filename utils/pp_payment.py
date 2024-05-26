from uuid import uuid4
from paypalrestsdk import Payment, WebProfile
from paypalrestsdk import Api as PaypalAPI
import os
from flask import url_for, session
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID")
SECRET_KEY = os.environ.get("PAYPAL_SECRET_KEY")

def transform_items(input_data):
    transformed_items = []

    for item in input_data:
        # Calculate the total price as quantity * amount, but amount should be per item already
        price_per_item = item['amount']  # The price is assumed to be given per single item

        # Create a new dictionary with the desired structure
        new_item = {
            'name': item['name'],
            'price': f'{price_per_item:.2f}',  # Format the price to two decimal places
            'currency': 'USD',
            'quantity': item['quantity']
        }
        transformed_items.append(new_item)

    return transformed_items



def SetExpressCheckout(items, profile=None, sandbox=False, client_id=CLIENT_ID, secret_key=SECRET_KEY):

    url_success = f"{url_for('success_payment', _external=True)}"
    url_cancel = f"{url_for('cancel_payment', _external=True)}"

    if sandbox:
        print("Sandbox mode is enabled")

    items = transform_items(items)

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
                          'currency': 'USD',
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
    
    for link in payment.links:
        if link.method == 'REDIRECT':
            redirect_url = link.href
            redirect_url += '&useraction=continue' #'&useraction=commit'
            break        
    session['paypal_link'] = redirect_url
    
    return redirect_url
