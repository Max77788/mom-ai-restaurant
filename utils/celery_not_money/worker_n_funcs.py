from celery import Celery
import logging
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv, find_dotenv
import os


load_dotenv(find_dotenv())

REDIS_URL = os.environ.get('REDISCLOUD_URL', 'redis://localhost:6379')

print(f"REDIS_URL chosen: {REDIS_URL}")

# Configure the Celery logger to output to console
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

app_celery = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)

def clear_celery_queue(celery_app):
    try:
        # Access the default queue and purge it
        celery_app.control.purge()
        print("Celery queue cleared successfully.")
    except Exception as e:
        print("Error clearing Celery queue:", e)

@app_celery.task
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