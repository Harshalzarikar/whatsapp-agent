# Override sqlite3 for Render compatibility with ChromaDB
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

from fastapi import FastAPI, Request, HTTPException, Query
import uvicorn
import os
import rag
import utils
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="WhatsApp RAG Chatbot")

WHATSAPP_VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "my_secure_verify_token")

from fastapi.responses import PlainTextResponse

@app.get("/whatsapp")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """
    Webhook verification endpoint for Meta WhatsApp Cloud API.
    """
    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        print("Webhook verified successfully!")
        return PlainTextResponse(content=str(hub_challenge))
    
    raise HTTPException(status_code=403, detail="Invalid verification token")

from fastapi import BackgroundTasks

def process_and_reply(sender_phone: str, message_text: str, phone_number_id: str):
    print(f"Processing message from {sender_phone} to {phone_number_id}: {message_text}", flush=True)
    # Process query with RAG pipeline
    if rag.rag_pipeline:
        try:
            answer = rag.rag_pipeline.get_answer(message_text)
        except Exception as e:
            print(f"Error generating answer: {e}", flush=True)
            answer = "I'm sorry, I encountered an error while processing your request."
    else:
        answer = "I'm currently unable to access my knowledge base. Please try again later."
    
    # Send reply using the Meta API
    utils.send_whatsapp_message(sender_phone, answer, phone_number_id)

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook endpoint to receive incoming messages from WhatsApp.
    """
    try:
        body = await request.json()
        print("INCOMING WEBHOOK PAYLOAD:")
        print(body)
    except Exception:
        return {"status": "ok"}
    
    # Check if this is a WhatsApp message event
    if body.get("object") == "whatsapp_business_account":
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                
                # Check if there are messages
                if "messages" in value and value["messages"]:
                    message = value["messages"][0]
                    
                    # Only process text messages
                    if message.get("type") == "text":
                        sender_phone = message.get("from")
                        message_text = message["text"]["body"]
                        
                        metadata = value.get("metadata", {})
                        phone_number_id = metadata.get("phone_number_id")
                        
                        # Process in background so we return 200 OK immediately to Meta
                        background_tasks.add_task(process_and_reply, sender_phone, message_text, phone_number_id)
                        
    return {"status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "ok", "rag_pipeline_loaded": rag.rag_pipeline is not None}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
