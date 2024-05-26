from pprint import pprint

from rapyd_utilities import make_request

response = make_request(method='get',
                        path=f'/v1/payment_methods/countries/US')

pprint(response)