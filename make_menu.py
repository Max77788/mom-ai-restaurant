import pandas as pd

df = pd.read_excel("default_menu/default_restaurant_menu.xlsx", engine='openpyxl')

html_menu = df.to_html(classes='table table-striped', index=False)

print(html_menu)

print(type(html_menu))