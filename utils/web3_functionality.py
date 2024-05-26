from web3 import Web3
import os
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())  

INFURA_POLYGON_PROJECT_ID = os.environ.get("INFURA_POLYGON_PROJECT_ID")

# Rapyd and Binance configuration
rapyd_api_key = os.environ.get('RAPYD_SANDBOX_SECRET_KEY')
#stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
"""
binance_api_key = os.environ.get('BINANCE_API_KEY')
binance_api_secret = os.environ.get('BINANCE_API_SECRET')
binance_client = Client(binance_api_key, binance_api_secret)
"""

def completion_on_binance_web3_wallet_withdraw(total_amount, web3_wallet_address):
    # Calculate amounts
    retained_amount = total_amount * 0.01
    purchase_amount = total_amount * 0.99

    # Initialize Binance client
    binance_client = Client(api_key=os.getenv('BINANCE_API_KEY'), api_secret=os.getenv('BINANCE_SECRET'))
    
    # Check USD balance
    usd_balance = float(binance_client.get_asset_balance(asset='USD')['free'])
    amount_to_spend = usd_balance  # You can modify this to spend a portion of your balance

    if usd_balance-10 < purchase_amount:
        return "Insufficient USD balance to buy USDT or there is no 10 dollars margin"

    # Buy USDT with the calculated purchase amount
    # Note: Ensure your account has the necessary permissions and balances for the trade
    order = binance_client.order_market_buy(
        symbol='USDT',  # Ensure the trading pair is correct e.g., 'BTCUSDT', 'ETHUSDT' depending on your currency
        quantity=purchase_amount
    )
   
    withdraw_result = binance_client.withdraw(
        asset='USDTUSD',
        address=web3_wallet_address,
        network='MATIC',  # Specifying the network as MATIC for Polygon
        amount=purchase_amount  # Withdraw the full USDT amount purchased
    )

    return withdraw_result


def create_web3_wallet():
    
    # Connect to Polygon
    w3 = Web3(Web3.HTTPProvider(INFURA_POLYGON_PROJECT_ID))

    # Check if the connection is successful
    if w3.isConnected():
        print("Connected to Polygon Network!")
    else:
        print("Failed to connect to the Polygon Network.")

    # Generate a new account
    account = w3.eth.account.create(os.urandom(32))  # Using urandom for entropy

    address = account.address

    private_key = account.privateKey.hex()
    
    # Return the account's address and private key
    return address, private_key

"""
def checkout_session_creation_stripe():
    try:
        # Create a new Checkout Session for the order
        # For full details see https://stripe.com/docs/api/checkout/sessions/create
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'T-shirt',
                        },
                        'unit_amount': 2000,
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel',
        )
        
        # Redirect to the URL for the Checkout
        print("Checkout URL:", checkout_session.url)
        return checkout_session.url
    except Exception as e:
        print("Error creating checkout session:", str(e))
"""