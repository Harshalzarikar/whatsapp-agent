# WhatsApp RAG Bot (with Waapi Integration)

This is a complete, autonomous WhatsApp agent that uses Retrieval-Augmented Generation (RAG) to answer questions based on a local knowledge base. It also supports dynamic learning: users can send PDF documents directly via WhatsApp, and the bot will instantly read, memorize, and use them to answer future questions!

## Technologies Used
- **FastAPI**: The web server that receives webhooks.
- **Waapi**: Unofficial WhatsApp API to send and receive messages without Meta Business restrictions.
- **Langchain & ChromaDB**: The AI logic and vector database that powers the bot's memory and intelligence.
- **Groq & Llama 3**: Lightning-fast Large Language Models for generating conversational answers.

## Setup Instructions

1. Clone this repository.
2. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.template` to `.env` and fill in your actual API keys:
   - `GROQ_API_KEY`: Get from Groq console.
   - `GEMINI_API_KEY`: Get from Google AI Studio.
   - `WAAPI_INSTANCE_ID`: Get from your Waapi dashboard.
   - `WAAPI_API_TOKEN`: Get from your Waapi dashboard.

4. Start the server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## Webhook Configuration
Once your server is running (e.g., deployed on Render), you must configure your Waapi Instance to forward incoming WhatsApp messages to your bot.
- Go to your Waapi Dashboard -> Settings -> Webhooks.
- Enter your public server URL followed by `/whatsapp` (e.g., `https://your-app.onrender.com/whatsapp`).
- Enable Webhooks.

---

## ⚠️ Important Note for the Founder (Waapi Trial vs Production)

Currently, this bot is running on a **Waapi Free Trial**. 

Waapi's free trial has a strict security block: **it will only allow the bot to send messages to the phone number that created the account.** If a customer texts the bot from a different phone number, Waapi will block the bot's reply and return a `403 Forbidden` error.

To get around this for testing purposes, we added a **Trial Override** in `utils.py`. When anyone texts the bot, the bot processes their message but redirects its answer directly to *your* phone number (the trial owner).

### How to Go Live for Customers (Production)

When you are ready to launch this bot to real customers, you must:

1. **Upgrade your Waapi account:** Purchase a paid plan on Waapi.app (starts around $3/month). This removes the destination blocks.
2. **Remove the Trial Override in the code:** 
   Open `utils.py` and delete the following lines (around lines 30-38):

   ```python
   # --- WAAPI TRIAL OVERRIDE ---
   # Force all replies to go to the registered trial phone number
   # This prevents the 403 Forbidden error when replying to other numbers during trial
   TRIAL_PHONE = "919284360901@c.us"
   if chat_id != TRIAL_PHONE:
       print(f"Waapi Trial Mode: Redirecting reply from {chat_id} to {TRIAL_PHONE}", flush=True)
       message_body = f"[Redirected reply to {chat_id}]\n\n{message_body}"
       chat_id = TRIAL_PHONE
   ```

3. **Deploy the updated code:** Once that override is deleted and your new code is deployed, the bot will naturally reply to whoever texted it!
