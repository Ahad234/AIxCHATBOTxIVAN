import os
import tempfile
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from google import genai

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN","8499063535:AAFyY7Fz1U_tXXJ6QK5yMI1FsOGzps7Hs78")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY","AIzaSyCoB2aGZxtZOl3LySSZbuUwzXcY--QcDmc")

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# Chatbot toggle (True = enabled)
chatbot_enabled = True

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Hello! I'm a Gemini AI bot.\n"
        "Commands:\n"
        "- `/chatbot on` or `/chatbot off` to enable/disable AI chat\n"
        "- `/sticker <prompt>` to create an AI sticker"
    )

# Chatbot toggle command
async def toggle_chatbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global chatbot_enabled
    if not context.args:
        await update.message.reply_text(f"🤖 Chatbot is currently {'ON' if chatbot_enabled else 'OFF'}. Use `/chatbot on` or `/chatbot off`.")
        return
    
    choice = context.args[0].lower()
    if choice == "on":
        chatbot_enabled = True
        await update.message.reply_text("✅ Chatbot enabled!")
    elif choice == "off":
        chatbot_enabled = False
        await update.message.reply_text("❌ Chatbot disabled!")
    else:
        await update.message.reply_text("⚠️ Use `/chatbot on` or `/chatbot off`.")

# Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global chatbot_enabled
    if not chatbot_enabled:
        return  # Ignore messages if chatbot is disabled

    user_message = update.message.text
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message
        )
        reply = response.text or "I couldn't generate a response."
    except Exception as e:
        reply = f"⚠️ Error: {e}"

    await update.message.reply_text(reply)

# AI Sticker generator
async def ai_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a prompt. Example: `/sticker cute cat`")
        return
    
    prompt = " ".join(context.args)
    await update.message.reply_text(f"🎨 Generating sticker: {prompt}...")

    try:
        # Generate image from Gemini
        image = client.models.generate_image(
            model="imagen-3.0-generate-001",
            prompt=prompt,
            size="512x512"
        )
        image_url = image.generated_images[0].image_uri

        # Download image
        img_data = requests.get(image_url).content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
            f.write(img_data)
            temp_path = f.name

        # Send as sticker
        with open(temp_path, "rb") as sticker_file:
            await update.message.reply_sticker(sticker_file)

        os.remove(temp_path)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Could not generate sticker: {e}")

# Main
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chatbot", toggle_chatbot))
    app.add_handler(CommandHandler("sticker", ai_sticker))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
