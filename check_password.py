import bcrypt
"""
# Function to hash a password
def hash_password(password):
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# Example usage
user_password = input("Enter your password: ")
hashed_password = hash_password(user_password)
print(f"Hashed Password: {hashed_password}")
"""

def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)

# Example usage
password_to_check = input("Re-enter your password: ")
if check_password(b'$2b$12$P.dH4tDCPQ6plL7Od5kl1uDegEtZioKLx.CChEuumdtSrLts8UL7a', password_to_check):
    print("Password is correct!")
else:
    print("Password is incorrect!")
