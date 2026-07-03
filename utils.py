import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Waapi credentials
WAAPI_INSTANCE_ID = os.environ.get('WAAPI_INSTANCE_ID')
WAAPI_API_TOKEN = os.environ.get('WAAPI_API_TOKEN')

def send_whatsapp_message(to_number: str, message_body: str, phone_number_id: str = None):
    """Sends a WhatsApp message using the Waapi API."""
    if not WAAPI_INSTANCE_ID or not WAAPI_API_TOKEN:
        print("Error: Waapi credentials not set in .env", flush=True)
        return False
        
    url = f"https://waapi.app/api/v1/instances/{WAAPI_INSTANCE_ID}/client/action/send-message"
    
    headers = {
        "Authorization": f"Bearer {WAAPI_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Format chat_id for waapi (remove any + sign)
    chat_id = to_number.replace("+", "")
    if not chat_id.endswith("@c.us"):
        chat_id = f"{chat_id}@c.us"
    
    data = {
        "chatId": chat_id,
        "message": message_body
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"Message sent successfully to {chat_id}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message: {e}")
        if e.response is not None:
            print(f"Response data: {e.response.text}")
        return False
