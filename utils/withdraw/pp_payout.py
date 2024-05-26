import requests
from requests.auth import HTTPBasicAuth
import random
import datetime

def generate_payout_string():
    # Get the current date
    now = datetime.datetime.now()
    year = now.year
    day = now.day
    month = now.month

    # Generate 5 random digits
    random_numbers = ''.join(random.choices('0123456789', k=5))

    # Construct the payout string
    payout_string = f"Payouts_{year}_{day:02d}{month:02d}{random_numbers}"
    
    return payout_string


def create_payout_request(receiver, value):
    sender_batch_id = f'"{generate_payout_string()}"'
    data = f'{{"sender_batch_header":{{"sender_batch_id":{sender_batch_id},"email_subject":"You have a payout!","email_message":"You have received a payout! Thanks for using MOM AI!"}},"items":[{{"recipient_type":"EMAIL","amount":{{"value":"{value}","currency":"USD"}},"note":"Thanks for cooperating with MOM AI!","receiver":"{receiver}"}}]}}'
    return data

def send_payout_pp(email, amount_usd, sandbox=True):
    
    if sandbox:
        url_to_send_on = 'https://api-m.sandbox.paypal.com/v1/payments/payouts'
    else:
        url_to_send_on = 'some_url_in_live'
    
    access_token = get_token()["access_token"]
    authorization = "Bearer "+ access_token
    #print(f"Authorization: {authorization}")

    headers = {
        'Content-Type': 'application/json',
        "Authorization": authorization,
    }
    
    amount_usd = f'{amount_usd:.2f}'

    #print(amount_usd)

    data = create_payout_request(email, amount_usd)

    #print(data)
    response = requests.post(url_to_send_on, headers=headers, data=data)
    #print("request sent")

    return response.json()

def pp_payout_test():
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer A21AAImN-fGvrR6t8W1Egc1vgsuR_XatfnfODxSTSu7UMyghbsIDFShgUTqUVw9NDL14QH1bhbWrVrqXe24bhfPDRih5v2hPA',
}

    data = '{ "sender_batch_header": { "sender_batch_id": "Payouts_2020_100142307", "email_subject": "You have a payout!", "email_message": "You have received a payout! Thanks for using our service!" }, "items": [ { "recipient_type": "EMAIL", "amount": { "value": "9.87", "currency": "USD" }, "note": "Thanks for your patronage!", "sender_item_id": "201403140201", "receiver": "receiver@example.com", "recipient_wallet": "RECIPIENT_SELECTED" } ] }'

    response = requests.post('https://api-m.sandbox.paypal.com/v1/payments/payouts', headers=headers, data=data)

    return response.json()

def get_token():
    url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US"
    }
    auth = HTTPBasicAuth("AcLO2sd8sjNaImmvySdZOoNHh6uqOs6_5K3KhcL5Hc6RLM-c29rXPQnXlvBiTQzlWRIO82M0kC_5rvYL", "ENvAm_l4dkmFEjpJhvBpe2y9rbP-rkLqFC8P45GoEi4R7LYEiL_f4I46ii5K4tGf5f7VL9Cs98SkGQqx")
    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(url, headers=headers, auth=auth, data=data)
    
    return response.json()

#test_paypal = send_payout_pp("sb-gz7oc15369232@personal.example.com", 115.37)
#print(test_paypal)