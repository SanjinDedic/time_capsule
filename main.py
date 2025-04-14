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
    key = combine_keys(user_key, SECRET_KEY)
    print(f"Key used for encryption: {key}")
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
        decoded_data = base64.b64decode(request.data + "==").decode("utf-8")
        data_dict = dict(item.split(': ') for item in decoded_data.split(', '))

        message = data_dict['message']
        time_created = int(data_dict['time_created'])
        time_revealed = int(data_dict['time_revealed'])
        locked_by = data_dict['locked_by']
        encryption_method = data_dict['encryption_method']
        user_key = data_dict['user_key']

        # Use UTC timestamps to avoid timezone and DST issues
        dt_time_created = datetime.datetime.fromtimestamp(
            time_created, tz=datetime.timezone.utc
        )
        dt_time_revealed = datetime.datetime.fromtimestamp(
            time_revealed, tz=datetime.timezone.utc
        )

        # Calculate difference in seconds
        difference_in_seconds = int(
            (dt_time_revealed - dt_time_created).total_seconds()
        )
        print(f"Difference in seconds: {difference_in_seconds}")

        # Allowed intervals in seconds (exactly 10, 100, or 1000 days)
        allowed_intervals = [10 * 86400, 100 * 86400, 1000 * 86400]
        print(f"Allowed intervals: {allowed_intervals}")

        # Use a simple direct comparison after fixing timezone issues
        valid_interval = difference_in_seconds in allowed_intervals

        # Alternatively, keep a small tolerance for rounding errors
        if not valid_interval:
            tolerance = 10  # 10 seconds tolerance for any remaining rounding errors
            for interval in allowed_intervals:
                if abs(difference_in_seconds - interval) <= tolerance:
                    valid_interval = True
                    print(f"Close match found: {difference_in_seconds} ≈ {interval}")
                    break

        if not valid_interval:
            print(f"No valid interval found. Difference: {difference_in_seconds}")
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
                    key = combine_keys(user_key, SECRET_KEY)
                    print(f"Key used for decryption: {key}")
                    decrypted_message = vigenere_decrypt(message, key)
                    return {
                        "message": decrypted_message,
                        "time_created": time_created,
                        "time_revealed": time_revealed,
                        "locked_by": locked_by,
                        "encryption_method": encryption_method,
                        "user_key": user_key,
                    }
                else:
                    raise HTTPException(
                        status_code=400, detail="Unsupported encryption method"
                    )
            else:
                # Format times in UTC to avoid timezone issues in display
                time_created_str = datetime.datetime.fromtimestamp(
                    time_created, tz=datetime.timezone.utc
                ).strftime("%d/%m/%Y %I:%M:%S %p UTC")
                time_revealed_str = datetime.datetime.fromtimestamp(
                    time_revealed, tz=datetime.timezone.utc
                ).strftime("%d/%m/%Y %I:%M:%S %p UTC")

                return {
                    "message": message,
                    "time_created": time_created_str,
                    "time_revealed": time_revealed_str,
                    "locked_by": locked_by,
                    "encryption_method": encryption_method,
                    "user_key": user_key,
                }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/vigenere_encrypt")
async def process_vigenere_encription(request: Encryption):
    try:
        encrypted_message = vigenere_encrypt(request.message, request.key)
        return {"encrypted_message": encrypted_message}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
