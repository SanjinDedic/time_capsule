# time_capsule
API for the time capsule application for the Victorian coding challenge

## Description
The Time Capsule application allows users to create encrypted messages that can only be decrypted after a specified time period. It uses the Vigenère cipher for encryption.

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation
1. Clone the repository:
```bash
git clone <repository-url>
cd time_capsule
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with a 100 character MASTER_KEY (Below is just an example)
```
MASTER_KEY=ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ
```

## Running the Application

### Starting the Server
Run the following command to start the FastAPI server:
```bash
uvicorn main:app --reload
```

The server will start, typically on port 8000. You should see output similar to:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [PID]
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### API Documentation
Once the server is running, you can access the API documentation at:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Using the Time Capsule Maker
The `capsule_maker.py` script is a client application that interacts with the API. To use it:

1. Make sure the server is running
2. Run the capsule maker:
```bash
python capsule_maker.py
```

3. Follow the prompts to:
   - Enter your message
   - Create an encryption key (alphabetic characters only)
   - Choose a locking period (10, 100, or 1000 days)
   - Enter your name

4. The script will output an encoded time capsule string
   - Keep this string to access your capsule later

### Accessing a Time Capsule
To access a time capsule, you can use the `submit-capsule` endpoint with the encoded capsule string. If the reveal time has passed, the message will be decrypted and returned.

Example using curl:
```bash
curl -X POST "http://127.0.0.1:8000/submit-capsule" -H "Content-Type: application/json" -d '{"data":"<your-encoded-time-capsule-string>"}'
```

## Security Note
This is a demonstration application and should not be used for sensitive data. The encryption method used (Vigenère cipher) is not considered secure by modern standards.
