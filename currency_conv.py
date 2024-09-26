from currency_converter import CurrencyConverter

# Initialize the CurrencyConverter class
c = CurrencyConverter()

# Convert from USD to EUR
rate = c.convert(1, 'THB', 'EUR')

print(f"1 THB is {rate} EUR")

