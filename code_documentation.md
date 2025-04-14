# Project Sitemap

## /home/slowturing/Documents/PROJECTS/time_capsule

[main.py](/home/slowturing/Documents/PROJECTS/time_capsule/main.py)
### /home/slowturing/Documents/PROJECTS/time_capsule/main.py
```
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
import base64
import time
import json
import os
from os.path import join, dirname
from dotenv import load_dotenv
import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

SECRET_KEY = os.environ.get("MASTER_KEY") # the MASTER_KEY is 100 characters long

class TimeCapsuleRequest(BaseModel):
    data: str

class Encryption(BaseModel):
    message: str
    key: str

alphabet=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
          'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

def shift_letter(letter, shift):
    global alphabet
    letter = letter.upper()
    if letter in alphabet:
        index = alphabet.index(letter)
        return alphabet[(index + shift) % 26]
    else:
        return letter

def combine_keys(user_key, my_key):
    combined_key = ""
    # Iterate over the length of the longer key
    for i in range(max(len(user_key), len(my_key))):
        if i < len(user_key):
            combined_key += user_key[i].upper()  # Add character from user key
        if i < len(my_key):
            combined_key += my_key[i].upper()    # Add character from your key
    return combined_key

def vigenere_decrypt(message, key):
    key = key.upper()
    decrypted_message = ""
    key_length = len(key)
    key_index = 0
    for char in message:
        if char.isalpha():
            shift = alphabet.index(key[key_index % key_length])
            decrypted_char = shift_letter(char, -shift)
            decrypted_message += decrypted_char
            key_index += 1
        else:
            decrypted_message += char
    return decrypted_message

def vigenere_encrypt(message, user_key):
    key = combine_keys(user_key,SECRET_KEY)
    key = key.upper()
    encrypted_message = ""
    key_length = len(key)
    key_index = 0
    for char in message:
        if char.isalpha():
            shift = alphabet.index(key[key_index % key_length])
            encrypted_char = shift_letter(char, shift)
            encrypted_message += encrypted_char
            key_index += 1
        else:
            encrypted_message += char
    return encrypted_message

@app.post("/submit-capsule")
async def process_time_capsule(request: TimeCapsuleRequest):
    try:
        decoded_data = base64.b64decode(request.data+"==").decode('utf-8')
        data_dict = dict(item.split(': ') for item in decoded_data.split(', '))

        message = data_dict['message']
        time_created = int(data_dict['time_created'])
        time_revealed = int(data_dict['time_revealed'])
        locked_by = data_dict['locked_by']
        encryption_method = data_dict['encryption_method']
        user_key = data_dict['user_key']
        dt_time_created = datetime.datetime.fromtimestamp(time_created)
        dt_time_revealed = datetime.datetime.fromtimestamp(time_revealed)

        difference_in_seconds = (dt_time_revealed - dt_time_created).total_seconds()

        allowed_intervals = [10 * 86400, 100 * 86400, 1000 * 86400]  # Convert days to seconds

        if difference_in_seconds not in allowed_intervals:
            return {
                "message": "WARNING! Time Capsule has been tampered",
                "time_created": time_created,
                "time_revealed": time_revealed,
                "locked_by": locked_by,
                "encryption_method": encryption_method,
                "user_key": user_key
            }
        else:
            current_time = int(time.time())

            if current_time >= time_revealed:
                if encryption_method == 'vigenere':
                   key=combine_keys(user_key,SECRET_KEY)
                   decrypted_message = vigenere_decrypt(message, key)
                   return {
                       "message": decrypted_message,
                       "time_created": time_created,
                       "time_revealed": time_revealed,
                       "locked_by": locked_by,
                       "encryption_method": encryption_method,
                       "user_key": user_key
                   }
                else:
                   raise HTTPException(status_code=400, detail="Unsupported encryption method")
            else:
               time_created_str = time.strftime('%d/%m/%Y %I:%M:%S %p', time.localtime(time_created))
               time_revealed_str = time.strftime('%d/%m/%Y %I:%M:%S %p', time.localtime(time_revealed))

               return {
                    "message": message,
                    "time_created": time_created_str,
                    "time_revealed": time_revealed_str,
                    "locked_by": locked_by,
                    "encryption_method": encryption_method,
                    "user_key": user_key
               }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.post("/vigenere_encrypt")
async def process_vigenere_encription(request: Encryption):
    try:
        encrypted_message = vigenere_encrypt(request.message,request.key)
        return { "encrypted_message" : encrypted_message }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```
[capsule_maker.py](/home/slowturing/Documents/PROJECTS/time_capsule/capsule_maker.py)
### /home/slowturing/Documents/PROJECTS/time_capsule/capsule_maker.py
```
import base64
import time
import os
import requests

vigenere_url = 'http://localhost:8000/time_capsule/vigenere_encrypt'

def make_time_capsule():
    print("Time Capsule Maker")
    print("--------------------")

    message = input("Enter your message: ")
    user_key = input("Enter the key (alphabetic letters only) : ")
    print("\nLocking Options:")
    print("1. 10 days")
    print("2. 100 days")
    print("3. 1000 days")
    lock_option = input("Choose the locking option (1-3): ")

    if lock_option == "1":
        lock_duration = 10 * 24 * 60 * 60  # 10 days in seconds
    elif lock_option == "2":
        lock_duration = 100 * 24 * 60 * 60  # 100 days in seconds
    elif lock_option == "3":
        lock_duration = 1000 * 24 * 60 * 60  # 1000 days in seconds
    else:
        print("Invalid locking option. Defaulting to 10 days.")
        lock_duration = 10 * 24 * 60 * 60  # 10 days in seconds

    data = {
        'message': message,
        'key': user_key
    }
    response = requests.post(vigenere_url, json=data)
    if response.status_code == 200:
        encrypted_message = response.json()['encrypted_message']
        print("encrypted message:", encrypted_message)
    else:
        print("An error occurred.")
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

# Run the time capsule maker
make_time_capsule()
```

## Files Processed Summary

Total files processed: 2

### List of Processed Files:
- /home/slowturing/Documents/PROJECTS/time_capsule/main.py
- /home/slowturing/Documents/PROJECTS/time_capsule/capsule_maker.py

## Explicitly Allowed Files

