import random
import string

key=4

def generate_salt(length=8):
    """Generate a random string of letters as the salt."""
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def caesar_cipher_with_salt(text, key=key, salt_length=8):
    # Generate a salt
    salt = generate_salt(salt_length)
    
    # Append the salt to the text
    salted_text = text + salt
    
    result = ""
    
    # Traverse each character in the salted text
    for char in salted_text:
        # Encrypt uppercase characters
        if char.isupper():
            result += chr((ord(char) + key - 65) % 26 + 65)
        # Encrypt lowercase characters
        elif char.islower():
            result += chr((ord(char) + key - 97) % 26 + 97)
        # If it's not a letter, leave it as it is
        else:
            result += char

    return result, salt  # Return both the ciphertext and the salt

