import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from groq import Groq
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# Simple Health Check Server for Render Web Service
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ။ Bot မှ ကြိုဆိုပါတယ်။ မေးချင်တာ မေးနိုင်ပါတယ်။")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": user_text}],
            model="llama-3.3-70b-versatile",
        )
        
        reply_text = chat_completion.choices[0].message.content
        formatted_message = f"```\n{reply_text}\n```"
        
        await update.message.reply_text(
            text=formatted_message, 
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

def main():
    # Start Health Check Server in a background thread
    Thread(target=run_health_check, daemon=True).start()

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot starting...")
    app.run_polling()

if __name__ == '__main__':
    main()
