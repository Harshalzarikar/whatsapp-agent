# Autonomous AI WhatsApp Agent

Welcome to your new AI-powered WhatsApp Agent! 

This system acts as an intelligent, autonomous customer service bot. It uses advanced AI (RAG - Retrieval-Augmented Generation) to understand incoming questions and provide highly accurate answers based on the knowledge base we have provided.

It also supports **Dynamic Learning**: If you or your customers send a PDF document to the bot over WhatsApp, the bot will instantly read, memorize, and use that document's information to answer future questions!

---

## 🚀 How to take your Bot Live (Action Required)

Currently, your bot is running on a **Waapi Free Trial**. 

Because of Waapi's strict trial limitations, the bot is currently locked in a "Sandbox Mode." This means it will only reply to the developer's registered testing phone number. If a real customer texts the bot right now, Waapi will block the bot from replying.

To unlock the bot and open it up to all your customers, follow these two simple steps:

### Step 1: Upgrade your Waapi Account
Purchase a basic paid subscription on your [Waapi.app](https://waapi.app/) account (starts at roughly $3/month). This will instantly lift the destination blocks on your API key.

### Step 2: Remove the "Trial Override" Code
Our developer added a temporary safety override in the code to allow testing during the free trial. Once you have upgraded your Waapi account, you just need to delete this override so the bot can reply to everyone natively.

1. Open the file `utils.py` in this codebase.
2. Scroll down to around **line 30**.
3. **Delete** this exact block of code:
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
4. Save the file and deploy the updated code to your server.

**That's it!** As soon as that code is removed, your bot will naturally reply to any phone number that texts it.

---

## 🛠️ Technical Setup (For your Server Admin)

If you ever need to restart the server or move it to a new host, here is how the technical environment is configured:

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Environment Variables:**
   You must have a `.env` file in the root directory with your secret keys:
   - `GROQ_API_KEY`: Your Groq AI key.
   - `GEMINI_API_KEY`: Your Google Gemini key (for embeddings).
   - `WAAPI_INSTANCE_ID`: From your Waapi dashboard.
   - `WAAPI_API_TOKEN`: From your Waapi dashboard.

3. **Start the Application:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

4. **Webhook:**
   Ensure your Waapi dashboard is configured to send Webhooks to `https://<your-server-url>/whatsapp`.
