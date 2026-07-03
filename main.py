# Override sqlite3 for Render compatibility with ChromaDB
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

from fastapi import FastAPI, Request, BackgroundTasks
import uvicorn
import os
import rag
import utils
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="WhatsApp RAG Chatbot")

def process_and_reply(sender_phone: str, message_text: str):
    print(f"Processing message from {sender_phone}: {message_text}", flush=True)
    # Process query with RAG pipeline
    if rag.rag_pipeline:
        try:
            answer = rag.rag_pipeline.get_answer(message_text)
        except Exception as e:
            print(f"Error generating answer: {e}", flush=True)
            answer = "I'm sorry, I encountered an error while processing your request."
    else:
        answer = "I'm currently unable to access my knowledge base. Please try again later."
    
    # Send reply using the Waapi API
    utils.send_whatsapp_message(sender_phone, answer)

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook endpoint to receive incoming messages from Waapi.
    """
    try:
        body = await request.json()
        print("INCOMING WAAPI WEBHOOK PAYLOAD:")
        print(body)
    except Exception:
        return {"status": "ok"}
    
    # Check if this is a message event from Waapi
    if body.get("event") == "message":
        data = body.get("data", {})
        message = data.get("message", {})
        
        # Ensure it's a text message or a chat message
        if message.get("type") in ["chat", "text"] and not message.get("fromMe"):
            sender_phone = message.get("from")
            message_text = message.get("body")
            
            if sender_phone and message_text:
                # Process in background so we return 200 OK immediately to Waapi
                background_tasks.add_task(process_and_reply, sender_phone, message_text)
                        
    return {"status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "ok", "rag_pipeline_loaded": rag.rag_pipeline is not None}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
