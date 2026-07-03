import os
import requests
import base64
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
        
    # --- WAAPI TRIAL OVERRIDE ---
    # Force all replies to go to the registered trial phone number
    # This prevents the 403 Forbidden error when replying to other numbers during trial
    TRIAL_PHONE = "919284360901@c.us"
    if chat_id != TRIAL_PHONE:
        print(f"Waapi Trial Mode: Redirecting reply from {chat_id} to {TRIAL_PHONE}", flush=True)
        message_body = f"[Redirected reply to {chat_id}]\n\n{message_body}"
        chat_id = TRIAL_PHONE
    
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

def download_waapi_media(message_obj: dict, filename: str = "temp_document.pdf") -> str:
    """Downloads media from a Waapi message object and saves it to a file."""
    if not WAAPI_INSTANCE_ID or not WAAPI_API_TOKEN:
        print("Error: Waapi credentials not set in .env", flush=True)
        return None
        
    url = f"https://waapi.app/api/v1/instances/{WAAPI_INSTANCE_ID}/client/action/download-media"
    
    headers = {
        "Authorization": f"Bearer {WAAPI_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    data = {
        "message": message_obj
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        resp_data = response.json()
        
        # Check if the response contains base64 data
        if "data" in resp_data and "data" in resp_data["data"]:
            base64_data = resp_data["data"]["data"]
        else:
            # Maybe it returns base64 string directly or under another key
            base64_data = resp_data.get("data", "")
            if isinstance(base64_data, dict):
                base64_data = base64_data.get("data", "") # Correct fallback
                
            if not base64_data and "base64" in resp_data:
                base64_data = resp_data["base64"]
                
        if not base64_data:
            print(f"Could not extract base64 data from response: {str(resp_data)[:200]}")
            return None
            
        # Decode base64
        # Remove data URI scheme if present (e.g. data:application/pdf;base64,...)
        if isinstance(base64_data, str) and base64_data.startswith("data:"):
            base64_data = base64_data.split(",")[1]
            
        file_bytes = base64.b64decode(base64_data)
        
        with open(filename, "wb") as f:
            f.write(file_bytes)
            
        print(f"Media downloaded and saved to {filename}")
        return filename
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to download media: {e}")
        if e.response is not None:
            print(f"Response data: {e.response.text}")
        return None
    except Exception as e:
        print(f"Error processing downloaded media: {e}")
        return None

