from functions import create_the_suitable_pathway, send_the_call_on_number_demo, get_conversational_pathway_data

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

create_the_suitable_pathway(restaurant_name, timezone, opening_hours, store_location, restaurant_menu)

# result = send_the_call_on_number_demo(where_to_call, restaurant_name, language)

# nodes_response = get_conversational_pathway_data()

# print(nodes_response, type(nodes_response))