import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Meta WhatsApp Cloud API credentials
WHATSAPP_API_TOKEN = os.environ.get('WHATSAPP_API_TOKEN')

def send_whatsapp_message(to_number: str, message_body: str, phone_number_id: str = None):
    """Sends a WhatsApp message using the Meta WhatsApp Cloud API."""
    if not WHATSAPP_API_TOKEN:
        print("Error: WhatsApp API token not set in .env", flush=True)
        return False
        
    # Fallback to env variable if not provided dynamically
    if not phone_number_id:
        phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
        
    if not phone_number_id:
        print("Error: WhatsApp Phone Number ID not provided", flush=True)
        return False
        
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    
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
