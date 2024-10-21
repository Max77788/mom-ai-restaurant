from square.client import Client as square_client_imp
from square.http.auth.o_auth_2 import BearerAuthCredentials
import uuid

def create_order_square(items_ordered, order_id, unique_azz_id, order_type, SQUARE_CLIENT):
    """
    Example of items_ordered: [{"name":"Item Name", "quantity":"2", "base_price_money":{"amount":777, "currency":"USD"}}, {...}, {...}]
    """

    result = SQUARE_CLIENT.orders.create_order(
    body = {
        "order": {
        "location_id": unique_azz_id,
        "reference_id": order_id,
        "line_items": items_ordered,
        "idempotency_key": uuid(),
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