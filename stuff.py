def remove_formatted_lines(menu_text):
    # Split the input text by lines
    lines = menu_text.split('\n')
    
    # Filter out lines that contain formatted text (bold text in this case)
    filtered_lines = [line for line in lines if '**' not in line and '#' not in line]
    
    # Join the remaining lines back into a single string
    result = '\n'.join(filtered_lines)
    
    return result

# Example usage
menu_text = """
We have these:

### Biryani
- **BIRYANI CHICKEN** - 15.34 EUR
- **BIRYANI LAMB** - 15.34 EUR
- **BIRYANI FISH** - 15.34 EUR
- **BIRYANI MIX** - 16.68 EUR
- **BIRYANI VEGETARIAN** - 15.34 EUR

### Shawarma
- **SHAWARMA CHICKEN** - 15.34 EUR
- **SHAWARMA LAMB** - 15.34 EUR
- **SHAWARMA MIX** - 16.68 EUR

### Doner
- **DONER CHICKEN** - 15.34 EUR
- **DONER LAMB** - 15.34 EUR
- **DONER MIX** - 16.68 EUR
- **DONER FALAFEL** - 15.34 EUR

### Salads
- **CHICKEN SALAD** - 14.67 EUR
- **LAMB SALAD** - 15.34 EUR
- **MIX SALAD** - 16.68 EUR
- **FISH SALAD** - 15.34 EUR

### Magnum
- **MAGNUM LAMB** - 15.34 EUR
- **MAGNUM CHICKEN** - 15.34 EUR
- **MAGNUM FISH** - 15.34 EUR
- **MAGNUM MIX** - 16.68 EUR

### Maria
- **LAMB MARIA** - 15.34 EUR
- **CHICKEN MARIA** - 15.34 EUR

### Burgers
- **BEEF BURGER** - 15.34 EUR
- **CHICKEN BURGER** - 15.34 EUR
- **LAMB BURGER** - 15.34 EUR
- **VEGETARIAN BURGER** - 15.34 EUR
- **DOUBLE BEEF BURGER** - 16.68 EUR
- **EGG BURGER** - 16.68 EUR

### Desserts and Extras
- **CHOCOLATE CAKE** - 5.03 EUR
- **BLACKBERRY CHEESECAKE** - 5.03 EUR
- **HUMMUS** - 5.96 EUR
- **BIG FRIES** - 6.63 EUR
- **KIDS RICE** - 9.71 EUR
- **KIDS FRIES** - 9.71 EUR

Something else?
"""

# Calling the function and printing the result
clean_menu = remove_formatted_lines(menu_text)
print(clean_menu)
