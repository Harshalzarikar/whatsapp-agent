import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Meta WhatsApp Cloud API credentials
WHATSAPP_API_TOKEN = os.environ.get('WHATSAPP_API_TOKEN')
WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')

def send_whatsapp_message(to_number: str, message_body: str):
    """Sends a WhatsApp message using the Meta WhatsApp Cloud API."""
    if not WHATSAPP_API_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        print("Error: WhatsApp API tokens not set in .env")
        return False
        
    url = f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": message_body
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"Message sent successfully to {to_number}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message: {e}")
        if e.response is not None:
            print(f"Response data: {e.response.text}")
        return False
