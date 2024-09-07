from currency_converter import CurrencyConverter

# Initialize the CurrencyConverter class
c = CurrencyConverter()

# Convert from USD to EUR
rate = c.convert(1, 'USD', 'EUR')

print(f"1 USD is {rate} EUR")

