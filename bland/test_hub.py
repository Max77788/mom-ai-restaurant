from functions import add_pathway_to_phone, create_the_suitable_pathway_script, send_the_call_on_number_demo, get_conversational_pathway_data, pathway_serving_a_to_z
import requests
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from pymongo import MongoClient
import os


where_to_call = "+3548425192"
restaurant_name = "Floppy Cockumber"
language = "en"

restaurant_name = "Matronins"
store_location = "Grushevskoho, 27, Vasylkiv, Ukraine"
opening_hours = """
                Monday - 9-23
                Tuesday - 9-23
                Wednesday - 9-23
                Thursday - 9-23
                Friday - 9-23
                Saturday - 15-1 AM
                Sunday - day off
                """
timezone = "GMT+2"
unique_azz_id = "matronins_nyje"

restaurant_menu = """ 
                    Format: Item Name   Item ingredients   Item price in EUR
                    BIRYANI CHICKEN	Yellow rice, chicken, mixed salad, tomato, red onion, cucumber, olive oil, spicy sauce, yogurt sauce.	15.34
                    BIRYANI LAMB	Yellow rice, lamb, mixed salad, tomato, red onion, cucumber, olive oil, spicy sauce, yogurt sauce.	15.34
                    BIRYANI FISH	Yellow rice, fish, mixed salad, tomato, cucumber, olive oil, red onion, yogurt sauce, spicy sauce.	15.34
                    BIRYANI MIX	Yellow rice, lamb, chicken, fish, mixed salad, tomato, red onion, cucumber, olive oil, spicy sauce, yogurt sauce.	16.68
                    BIRYANI VEGETARIAN	Falafel, Hummus, yellow rice, mixed salad, red onion, tomato, cucumber, yogurt sauce, spicy sauce.	15.34
                    SHAWARMA CHICKEN	Tortilla bread, marinated chicken in Arabic spices, fries, pomegranate molasses, mayonnaise.	15.34
                    SHAWARMA LAMB	Tortilla bread, marinated lamb in Arabic spices, mayonnaise, pomegranate molasses, fries.	15.34
                    SHAWARMA MIX	Tortilla bread, marinated chicken and lamb in Arabic spices, fries, mayonnaise, pomegranate molasses.	16.68
                    DONER CHICKEN	Pita bread, chicken, mixed salad, garlic sauce, spicy sauce, French fries.	15.34
                    DONER LAMB	Bread, lamb, mixed salad, tomato, red onion, French fries, garlic sauce, spicy sauce.	15.34
                    DONER MIX	Pita bread, chicken, lamb, mixed salad, spicy sauce, garlic sauce, French fries.	16.68
                    DONER FALAFEL	Pita bread, hummus, falafel, mixed salad, tomato, red onion, cucumber, French fries, yogurt sauce, spicy sauce.	15.34
                    CHICKEN SALAD	Mixed salad, tomato, red onion, cucumber, olive oil, chicken, spicy sauce, garlic sauce.	14.67
                    LAMB SALAD	Mixed salad, tomato, red onion, cucumber, olive oil, lamb, spicy sauce, garlic sauce.	15.34
                    MIX SALAD	Mixed salad, tomato, red onion, cucumber, olive oil, chicken, lamb, spicy sauce, garlic sauce.	16.68
                    FISH SALAD	Mixed salad, tomato, red onion, cucumber, olive oil, fish, spicy sauce, yogurt sauce.	15.34
                    MAGNUM LAMB	French fries, lamb, mixed salad, red onion, cucumber, tomato, olive oil, spicy sauce, garlic sauce.	15.34
                    MAGNUM CHICKEN	French fries, chicken, mixed salad, red onion, cucumber, tomato, olive oil, spicy sauce, garlic sauce.	15.34
                    MAGNUM FISH	French fries, fish, mixed salad, red onion, cucumber, tomato, olive oil, spicy sauce, garlic sauce.	15.34
                    MAGNUM MIX	French fries, chicken, lamb, mixed salad, red onion, cucumber, tomato, olive oil, spicy sauce, garlic sauce.	16.68
                    LAMB MARIA	Minced lamb meat marinated in Arabic spices, mozzarella cheese, French fries, garlic sauce.	15.34
                    CHICKEN MARIA	Minced chicken meat marinated in Arabic spices, mozzarella cheese, French fries, garlic sauce.	15.34
                    BEEF BURGER	Minced beef, cheese, lettuce, tomato, red onion, special hamburger sauce, spicy sauce, fries.	15.34
                    CHICKEN BURGER	Minced chicken, cheese, lettuce, tomato, onion, special hamburger sauce, spicy sauce, fries.	15.34
                    LAMB BURGER	Minced lamb, cheese, lettuce, tomato, red onion, special hamburger sauce, spicy sauce, fries.	15.34
                    VEGETARIAN BURGER	Chickpeas burger, cheese, lettuce, tomato, red onion, special hamburger sauce, spicy sauce, fries.	15.34
                    DOUBLE BEEF BURGER	Double minced beef, cheese, lettuce, tomato, red onion, special hamburger sauce, spicy sauce, fries.	16.68
                    EGG BURGER	Chicken, lamb or beef, cheese, lettuce, tomato, red onion, special hamburger sauce, spicy sauce, fries.	16.68
                    CHOCOLATE CAKE	Deepfrozen round choco cake, filled with choco filling, finished with a choco topping, decorated with chocolate drops.	5.03
                    BLACKBERRY CHEESECAKE	A plain gluten free biscuit base topped with luxury baked cheesecake.	5.03
                    HUMMUS	Chickpea, Tahini (sesame seeds), Lemon, Olive oil, Salt, Sumac, Cumin and Allergy Warning: Tahini (Sesame Seeds).	5.96
                    BIG FRIES	Big Fries.	6.63
                    KIDS RICE	Kids Rice.	9.71
                    KIDS FRIES	Kids Fries.	9.71

                  """

def test_posting_voice_order():
    # Define the endpoint URL
    url = "https://mom-ai-restaurant-stage-1709afd7171d.herokuapp.com/post-voice-order"

    # Define the request payload
    payload = {
        "unique_azz_id": "dominos_YCcs",
        "array_of_ordered_items": [
            {"name": "MAGNUM CHICKEN ROLL", "quantity":3, "price": 2190},
            {"name": "Shawarma Chicken", "quantity":3,  "price": 2290}
        ],
        "name": "John Doe",
        "from_number": "+380507773477"
    }

    # Send the POST request
    response = requests.post(url, json=payload)

    # Check the response
    if response.status_code == 200:
        print("Order placed successfully")
        print("Response:", response.json())
    else:
        print("Failed to place order")
        print("Response:", response.text)

import re

def replace_markdown_images(text):
    # Regular expression pattern to find ![text](url)
    pattern = r'!\[(.*?)\]\((.*?)\)'
    
    # Function to replace the matched pattern with the desired <img> tag
    def replace_match(match):
        alt_text = match.group(1)
        src_url = match.group(2)
        return f'<img src="{src_url}" alt="Image of {alt_text}" width="170" height="auto">'
    
    # Use re.sub to replace all occurrences of the pattern
    return re.sub(pattern, replace_match, text)



def extract_text_from_file(file_path):
    file_extension = file_path.split('.')[-1].lower()

    if file_extension == 'txt':
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            encoding = result['encoding']
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    
    elif file_extension == 'xlsx':
        df = pd.read_excel(file_path)
        return df.to_string(index=False)
    
    elif file_extension == 'docx':
        doc = docx.Document(file_path)
        full_text = []
        for paragraph in doc.paragraphs:
            full_text.append(paragraph.text)
        return '\n'.join(full_text)
    
    elif file_extension == 'pdf':
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = []
            for page in reader.pages:
                text.append(page.extract_text())
            return '\n'.join(text)
    
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")



# Example usage:
# text = extract_text_from_file('menu_examples/menu.xlsx')
# print(text)


# Example usage
#text = "Check out this image ![SHAWARMA MIX](https://i.ibb.co/P90SVMs/800-6012d21eefaf5.jpg)"
#updated_text = replace_markdown_images(text)
#print(updated_text)








mongodb_connection_string = os.environ.get("MONGODB_CONNECTION_URI")

# Connect to MongoDB
client_db = MongoClient(mongodb_connection_string)

# Specify the database name
db_mongo = client_db['MOM_AI_Restaurants']

# Specify the collection name
collection = db_mongo[os.environ.get("DB_VERSION")]

dicts = collection.find_one({"unique_azz_id":unique_azz_id}).get("html_menu_tuples")

#item_lines = [f"Item Name - {item['Item Name']}\nItem Description - {item['Item Description']}\nItem Price - {item['Item Price (EUR)']}\n\n\n" for item in dicts]

item_lines = [{"Item Name" :item['Item Name'], "Item Description": item['Item Description'], "Item Price": item['Item Price (EUR)']} for item in dicts]

print(item_lines)


# success = add_pathway_to_phone("+14153017040", "5c01d028-8f2b-4560-8aec-ddad5de31a9f", "uk")

# success = pathway_serving_a_to_z(restaurant_name, store_location, opening_hours, timezone, restaurant_menu, unique_azz_id)

# print("Success??? ", success)

#test_posting_voice_order()

# create_the_suitable_pathway_script(restaurant_name, timezone, opening_hours, store_location, restaurant_menu, unique_azz_id)

# result = send_the_call_on_number_demo(where_to_call, restaurant_name, language)

# nodes_response = get_conversational_pathway_data()

# print(nodes_response, type(nodes_response))