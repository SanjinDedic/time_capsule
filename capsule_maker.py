import base64
import time
import os
import requests

vigenere_url = 'http://localhost:8000/vigenere_encrypt'

def make_time_capsule():
    print("Time Capsule Maker")
    print("--------------------")

    message = input("Enter your message: ")
    
    # Get and validate the key
    while True:
        user_key = input("Enter the key (alphabetic letters only) : ")
        # Check if key contains only alphabetic characters
        if not user_key:
            print("Error: Key cannot be empty.")
            continue
        if not user_key.isalpha():
            print("Error: Key must contain only alphabetic characters (A-Z, a-z). No spaces or special characters allowed.")
            continue
        break  # Key is valid, exit the loop

    print("\nLocking Options:")
    print("1. 10 days")
    print("2. 100 days")
    print("3. 1000 days")
    
    # Get and validate the lock option
    while True:
        lock_option = input("Choose the locking option (1-3): ")
        if lock_option in ["1", "2", "3"]:
            break
        print("Invalid locking option. Please enter 1, 2, or 3.")

    if lock_option == "1":
        lock_duration = 10 * 24 * 60 * 60  # 10 days in seconds
    elif lock_option == "2":
        lock_duration = 100 * 24 * 60 * 60  # 100 days in seconds
    else:  # lock_option == "3"
        lock_duration = 1000 * 24 * 60 * 60  # 1000 days in seconds

    data = {
        'message': message,
        'key': user_key
    }
    
    try:
        response = requests.post(vigenere_url, json=data)
        if response.status_code == 200:
            encrypted_message = response.json()['encrypted_message']
            print("Encrypted message:", encrypted_message)
        else:
            try:
                error_detail = response.json().get('detail', 'Unknown error')
                print(f"Error: {error_detail}")
            except:
                print(f"Error {response.status_code}: {response.text}")
            return
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure it's running at", vigenere_url)
        return
    except Exception as e:
        print(f"Error: {str(e)}")
        return

    encryption_method = "vigenere"

    time_created = int(time.time())
    time_revealed = time_created + lock_duration
    
    locked_by = input("Enter your name: ")

    time_capsule_data = (
        f"message: {encrypted_message}, "
        f"time_created: {time_created}, "
        f"time_revealed: {time_revealed}, "
        f"locked_by: {locked_by}, "
        f"encryption_method: {encryption_method}, "
        f"user_key: {user_key}"
    )
    encoded_data = base64.b64encode(time_capsule_data.encode('utf-8')).decode('utf-8')

    print("\nYour digital time capsule:")
    print(encoded_data)
    
    # Calculate and display the reveal date
    reveal_date = time.strftime('%d/%m/%Y %I:%M:%S %p', time.localtime(time_revealed))
    print(f"\nYour message will be revealed on: {reveal_date}")

# Run the time capsule maker
if __name__ == "__main__":
    make_time_capsule()