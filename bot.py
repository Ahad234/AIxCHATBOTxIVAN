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
BOT_TOKEN = os.getenv("BOT_TOKEN", "8490850898:AAGqe1UJi6z9SDyQ06Dg-4XzJNUEgGPZLGA")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCoB2aGZxtZOl3LySSZbuUwzXcY--QcDmc")

OWNER_NAME = "- 𝐼 ꪜ ꪖ ꪀ"  # <--- Bot owner name

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

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
        "CAACAgUAAxkBAAEBH1xmQjZAI49byo2q7DZp1G4pyhBk9WwAApYBAAJdH3lVTy4xZa4qAiEuBA"
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

# =============== REACTION LOGIC ==================
def get_reaction(message: str):
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

# =============== COMMAND HANDLERS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Namaste! Main ek AI chatbot hoon. /chatbot enable karo baat karne ke liye."
    )

async def enable_chatbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    enabled_chats.add(chat_id)
    await update.message.reply_text("✅ Chatbot enabled!")

async def disable_chatbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    enabled_chats.discard(chat_id)
    await update.message.reply_text("❌ Chatbot disabled!")

# =============== MESSAGE HANDLER ==================
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.message.from_user.first_name
    text = update.message.text

    if chat_id not in enabled_chats:
        return

    # Special Owner Question
    if any(word in text.lower() for word in ["who made you", "owner", "creator"]):
        reply = f"Mujhe {OWNER_NAME} ne banaya hai! 🔥"
    else:
        # AI Reply
        try:
            response = model.generate_content(
                f"Reply in Hinglish (Hindi in English letters), friendly, human-like. No NSFW. User: {text}"
            )
            reply = response.text.strip()
        except Exception as e:
            logging.error(f"Gemini error: {e}")
            reply = "Arre bhai, thoda error aa gaya! 😅"

    await update.message.reply_text(f"{user}, {reply}")

    # Send Sticker or GIF
    reaction = get_reaction(text)
    if reaction.startswith("http"):
        await update.message.reply_animation(reaction)
    else:
        await update.message.reply_sticker(reaction)

# =============== MAIN ==================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chatbot", enable_chatbot, filters.Regex("^enable$")))
    app.add_handler(CommandHandler("chatbot", disable_chatbot, filters.Regex("^disable$")))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    logging.info("Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
