import requests
from pp_payout import get_token

token = get_token()["access_token"]

autorization = "Bearer " + token



headers = {
    'Content-Type': 'application/json',
    'Authorization': autorization,
}

params = (
    ('page', '1'),
    ('page_size', '5'),
    ('total_required', 'true'),
)

response = requests.get('https://api-m.sandbox.paypal.com/v1/payments/payouts/3AUF3VNRXBSAA', headers=headers, params=params)

print(response.json())

#NB. Original query string below. It seems impossible to parse and
#reproduce query strings 100% accurately so the one below is given
#in case the reproduced version is not "correct".
# response = requests.get('https://api-m.sandbox.paypal.com/v1/payments/payouts/LEP6947CGTKRL?page=1&page_size=5&total_required=true', headers=headers)
