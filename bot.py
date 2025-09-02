import os
import random
import logging
from telegram import Update, ChatAction
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
import google.generativeai as genai

# =============== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

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

# =============== REACTIONS ==================
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
        "🤖 Namaste! Main ek AI chatbot hoon.\nUse `/chatbot enable` or `/chatbot disable`."
    )

async def chatbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not context.args:
        await update.message.reply_text("⚙️ Use `/chatbot enable` or `/chatbot disable`.")
        return
    
    command = context.args[0].lower()
    if command == "enable":
        enabled_chats.add(chat_id)
        await update.message.reply_text("✅ Chatbot enabled!")
    elif command == "disable":
        enabled_chats.discard(chat_id)
        await update.message.reply_text("❌ Chatbot disabled!")
    else:
        await update.message.reply_text("⚙️ Unknown option. Use `/chatbot enable` or `/chatbot disable`.")

# =============== CHAT HANDLER ==================
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.message.from_user.first_name
    text = update.message.text

    if chat_id not in enabled_chats:
        return

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    if any(word in text.lower() for word in ["who made you", "owner", "creator"]):
        reply = f"Mujhe {OWNER_NAME} ne banaya hai! 🔥"
        await update.message.reply_text(f"{user}, {reply}")
        return

    try:
        response = model.generate_content(
            f"Reply in Hinglish (Hindi in English letters), friendly, human-like. No NSFW. User: {text}",
            stream=True
        )

        full_reply = ""
        sent_partial = False
        async for chunk in response:
            if chunk.candidates and chunk.candidates[0].content.parts:
                text_chunk = chunk.candidates[0].content.parts[0].text
                full_reply += text_chunk

                # Send first 40+ chars early
                if len(full_reply) > 40 and not sent_partial:
                    await update.message.reply_text(f"{user}, {full_reply}")
                    sent_partial = True

        # If no partial was sent, send full
        if not sent_partial:
            await update.message.reply_text(f"{user}, {full_reply}")

    except Exception as e:
        logging.error(f"Gemini error: {e}")
        await update.message.reply_text("Arre bhai, thoda error aa gaya! 😅")

    # Send sticker or GIF
    reaction = get_reaction(text)
    if reaction.startswith("http"):
        await update.message.reply_animation(reaction)
    else:
        await update.message.reply_sticker(reaction)

# =============== MAIN ==================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chatbot", chatbot))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    logging.info("Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
