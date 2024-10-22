from square.client import Client as square_client_imp
from square.http.auth.o_auth_2 import BearerAuthCredentials
import uuid

def create_order_square(items_ordered, order_id, unique_azz_id, order_type, SQUARE_CLIENT, location_id = "L9WRDD8SZAN0R"):
    """
    Example of items_ordered: [{"name":"Item Name", "quantity":"2", "base_price_money":{"amount":777, "currency":"USD"}}, {...}, {...}]
    """

    result = SQUARE_CLIENT.orders.create_order(
    body = {
        "order": {
        "location_id": location_id,
        "reference_id": unique_azz_id+"_"+order_id,
        "line_items": items_ordered,
        "idempotency_key": uuid.uuid4(),
        "metadata": {
            "order_type": order_type
        }
        }
        }
    )

    if result.is_success():
        print(result.body)
    elif result.is_error():
        print(result.errors)

square_client = square_client_imp(
        bearer_auth_credentials=BearerAuthCredentials(
        access_token="EAAAlo2_hNko81gg4jrU1ErixO5dS_RnAgbZzEtIZDOZnuclIVSEnnmPyy5sS-n0"
        ),
        environment="production")

"""
# Define the items ordered and other parameters
items_ordered = [
    {"name": "Item Name", "quantity": "2", "base_price_money": {"amount": 777, "currency": "USD"}},
    {"name": "Item Name 2", "quantity": "3", "base_price_money": {"amount": 888, "currency": "USD"}}
]
order_id = "order123"
unique_azz_id = "L9WRDD8SZAN0R"
order_type = "dine-in"




# Call the function
create_order_square(items_ordered, order_id, unique_azz_id, order_type, square_client)
"""

result = square_client.orders.retrieve_order(
  order_id = "0vcF29MfbjlUcemrw0iYQQpjpxHZ"
)

if result.is_success():
  print(result.body)
elif result.is_error():
  print(result.errors)

