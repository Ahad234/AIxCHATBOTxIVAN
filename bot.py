import os
import random
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
import google.generativeai as genai

# =============== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Chatbot toggle storage
enabled_chats = set()

# =============== LOGGING ==================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# =============== STICKERS & GIFS ==================
STICKERS = {
    "funny": [
        "CAACAgUAAxkBAAEBH1hmQjY0AAGaP8kKqZ2MTXShUMQJtFMAAvcBAAJdH3lV8A8g8T9R3uIuBA",
        "CAACAgUAAxkBAAEBH1pmQjY7Z3QY7gABRQZjNn2Gp09u2qcAAkMBAAJdH3lVUNXY8x_gD0wuBA",
        "CAACAgUAAxkBAAEBH1xmQjZAI49byo2q7DZp1G4pyhBk9WwAApYBAAJdH3lVTy4xZa4qAiEuBA",
        "CAACAgUAAxkBAAECHYdlmQjv7u0o56M7Qm3Wc1W7W8hzPgACawMAAladvQZxQvP1DjY8ViME",
        "CAACAgUAAxkBAAECHYtlmQjyK8gFQb5QpO2oP0-94GJjMgACbgMAAladvQYow-VqTXQJNSME",
        "CAACAgUAAxkBAAECHZBlmQj2OlfOsvhHPMWdnR0oRLnU3AACbwMAAladvQZ2qZ6qHYQ8zSME"
    ],
    "lol": [
        "CAACAgUAAxkBAAECHa1lmlaugh1AC",
        "CAACAgUAAxkBAAECHa9lmlaugh2AC"
    ],
    "angry": [
        "CAACAgUAAxkBAAECHbFlmangry1AC",
        "CAACAgUAAxkBAAECHbNlmlangry2AC"
    ],
    "love": [
        "CAACAgUAAxkBAAECHbVlmlove1AC",
        "CAACAgUAAxkBAAECHbdlmlove2AC"
    ],
    "chill": [
        "CAACAgUAAxkBAAECHbllmchill1AC",
        "CAACAgUAAxkBAAECHbtlmchill2AC"
    ]
}

GIFS = [
    "https://media.giphy.com/media/3o7aD2saalBwwftBIY/giphy.gif",
    "https://media.giphy.com/media/26AHONQ79FdWZhAI0/giphy.gif",
    "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
    "https://media.giphy.com/media/26ufdipQqU2lhNA4g/giphy.gif",
    "https://media.giphy.com/media/xT9IgIc0lryrxvqVGM/giphy.gif",
    "https://media.giphy.com/media/3o6Zt481isNVuQI1l6/giphy.gif",
    "https://media.giphy.com/media/l41lFw057lAJQMwg0/giphy.gif",
    "https://media.giphy.com/media/5GoVLqeAOo6PK/giphy.gif",
    "https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif",
    "https://media.giphy.com/media/ICOgUNjpvO0PC/giphy.gif"
]

# =============== HELPERS ==================
def get_reaction(message):
    msg = message.lower()
    if any(word in msg for word in ["love", "❤️", "meri jaan", "baby", "bhabhi"]):
        return random.choice(STICKERS["love"])
    elif any(word in msg for word in ["angry", "gussa", "😡", "mad"]):
        return random.choice(STICKERS["angry"])
    elif any(word in msg for word in ["lol", "haha", "rofl", "😂", "😆"]):
        return random.choice(STICKERS["lol"])
    elif any(word in msg for word in ["chill", "relax", "cool", "😎"]):
        return random.choice(STICKERS["chill"])
    elif random.choice([True, False]):
        return random.choice(GIFS)
    else:
        return random.choice(STICKERS["funny"])

def is_nsfw(message):
    banned_words = ["nude", "porn", "xxx", "sex", "boobs", "cock", "pussy"]
    return any(word in message.lower() for word in banned_words)

# =============== COMMAND HANDLERS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Namaste! Main ek AI chatbot hu.\n"
        "Type /chatbot enable to start chatting.\n"
        "Type /chatbot disable to stop me."
    )

async def chatbot_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if len(context.args) > 0:
        if context.args[0].lower() == "enable":
            enabled_chats.add(chat_id)
            await update.message.reply_text("✅ Chatbot enabled!")
        elif context.args[0].lower() == "disable":
            enabled_chats.discard(chat_id)
            await update.message.reply_text("❌ Chatbot disabled!")
    else:
        await update.message.reply_text("Usage: /chatbot enable or /chatbot disable")

# =============== MAIN CHAT HANDLER ==================
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text
    user = update.message.from_user.first_name

    if chat_id not in enabled_chats:
        return

    if is_nsfw(text):
        await update.message.reply_text("⚠️ Bhai, ye baatein allowed nahi hain!")
        return

    try:
        prompt = f"User({user}) said: {text}\nReply in Hinglish, friendly tone, like a real human bro:"
        response = model.generate_content(prompt)
        reply = response.text.strip()

        await update.message.reply_text(f"{reply}")

        # Sticker/GIF Reaction
        reaction = get_reaction(text)
        if "http" in reaction:
            await update.message.reply_animation(reaction)
        else:
            await update.message.reply_sticker(reaction)

    except Exception as e:
        await update.message.reply_text("⚠️ Error in AI response.")
        print(e)

# =============== MAIN APP ==================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chatbot", chatbot_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🤖 Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
