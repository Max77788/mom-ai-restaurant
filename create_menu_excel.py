import pandas as pd

# Define the menu data
menu_data = {
    "Item Name": [
        "Biryani Chicken", "Biryani Lamb", "Biryani Fish", "Biryani Mix", "Biryani Vegetarian",
        "Shawarma Chicken", "Shawarma Lamb", "Shawarma Mix",
        "Doner Chicken", "Doner Lamb", "Doner Mix", "Doner Falafel",
        "Chicken Salad", "Lamb Salad", "Mix Salad", "Fish Salad",
        "Magnum Lamb", "Magnum Chicken", "Magnum Fish", "Magnum Mix",
        "Lamb Maria", "Chicken Maria",
        "Beef Burger", "Chicken Burger", "Lamb Burger", "Vegetarian Burger", "Double Beef Burger", "Egg Burger",
        "Chocolate Cake", "Blackberry Cheesecake",
        "Hummus", "Big Fries", "Kids Rice", "Kids Fries"
    ],
    "Description": [
        "Yellow rice, chicken, mixed salad, tomato, red onion, cucumber, olive oil, spicy sauce, yogurt sauce.",
        "Yellow rice, lamb, mixed salad, tomato, red onion, cucumber, olive oil, spicy sauce, yogurt sauce.",
        "Yellow rice, fish, mixed salad, tomato, cucumber, olive oil, red onion, yogurt sauce, spicy sauce.",
        "Yellow rice, lamb, chicken, fish, mixed salad, tomato, red onion, cucumber, olive oil, spicy sauce, yogurt sauce.",
        "Falafel, Hummus, yellow rice, mixed salad, red onion, tomato, cucumber, yogurt sauce, spicy sauce.",
        "Tortilla bread, marinated chicken in Arabic spices, fries, pomegranate molasses, mayonnaise.",
        "Tortilla bread, Marinated lamb in Arabic spices, mayonnaise, pomegranate molasses, fries.",
        "Tortilla bread, Marinated chicken and lamb in Arabic spices, fries, mayonnaise, pomegranate molasses.",
        "Pita bread, chicken, mixed salad, garlic sauce, spicy sauce, French fries",
        "Bread, lamb, mixed salad, tomato, red onion, French fries, garlic sauce, spicy sauce.",
        "Pita bread, chicken, lamb, mixed salad, spicy sauce, garlic sauce, French fries",
        "Pita bread, hummus, falafel, mixed salad, tomato, red onion, cucumber, French fries, yogurt sauce, spicy sauce.",
        "Mixed salad, tomato, red onion, cucumber, olive oil, chicken, spicy sauce, garlic sauce.",
        "Mixed salad, tomato, red onion, cucumber, olive oil, lamb, spicy sauce, garlic sauce.",
        "Mixed salad, tomato, red onion, cucumber, olive oil, chicken, lamb, spicy sauce, garlic sauce.",
        "Mixed salad, tomato, red onion, cucumber, olive oil, fish, spicy sauce, yogurt sauce.",
        "French fries, lamb, mixed salad, red onion, cucumber, tomato, olive oil, spicy sauce, garlic sauce.",
        "French fries, chicken, mixed salad, red onion, cucumber, tomato, olive oil, spicy sauce, garlic sauce.",
        "French fries, fish, mixed salad, red onion, cucumber, tomato, olive oil, spicy sauce, garlic sauce.",
        "French fries, chicken, lamb, mixed salad, red onion, cucumber, tomato, olive oil, spicy sauce, garlic sauce.",
        "Minced lamb meat marinated in Arabic spices, mozzarella cheese, French fries, garlic sauce.",
        "Minced chicken meat marinated in Arabic spices, mozzarella cheese, French fries, garlic sauce.",
        "Minced beef, cheese, lettuce, tomato, red onion, special hamburger sauce, spicy sauce, fries.",
        "Minced chicken, cheese, lettuce, tomato, onion, special hamburger sauce, spicy sauce, fries.",
        "Minced lamb, cheese, lettuce, tomato, red onion, special hamburger sauce, spicy sauce, fries.",
        "Chickpeas burger, cheese, lettuce, tomato, red onion, special hamburger sauce, spicy sauce, fries.",
        "Double minced beef, cheese, lettuce, tomato, red onion, special hamburger sauce, spicy sauce, fries.",
        "(chicken or lamb or beef) cheese, lettuce, tomato, red onion, special hamburger sauce, spicy sauce, fries.",
        "Deep-frozen round choco cake, filled with choco filling, finished with a choco topping, decorated with chocolate drops.",
        "A plain gluten-free biscuit base topped with luxury baked cheesecake topped."
    ],
    "Price EUR": [
        15.23, 15.23, 15.23, 16.53, 15.23,
        15.23, 15.23, 16.53,
        15.23, 15.23, 15.23, 15.23,
        14.63, 15.23, 15.23, 15.23,
        15.23, 15.23,
        15.23, 15.23, 15.23, 15.23, 16.53, 16.53,
        15.03, 15.03,
        5.93, 6.63, 9.73, 9.73
    ]
}

# Convert ISK to EUR
for i in range(len(menu_data["Price EUR"])):
    menu_data["Price EUR"][i] *= 0.0067

# Create DataFrame
df = pd.DataFrame(menu_data)

# Write to Excel
df.to_excel("restaurant_menu.xlsx", index=False, engine='openpyxl')
print("Excel file created successfully!")