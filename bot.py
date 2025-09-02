import os
import random
import logging
import asyncio
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
import google.generativeai as genai

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_KEY")
OWNER_NAME = os.getenv("OWNER_NAME", "Baby")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

enabled_chats = set()
last_replies = {}  # Track last reply per chat to avoid repetition

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# ================= MEDIA =================
VOICE_NOTES = {
    "romantic": ["voices/hey_baby.ogg", "voices/miss_you.ogg", "voices/love_you.ogg"],
    "cute": ["voices/giggle.ogg", "voices/aww.ogg", "voices/hehe.ogg"],
    "sad": ["voices/sad.ogg", "voices/miss_you_sad.ogg"]
}

SELFIES = ["images/selfie1.jpg", "images/selfie2.jpg", "images/selfie3.jpg"]
GIFS = ["images/love1.gif", "images/love2.gif", "images/love3.gif"]
STICKERS = ["stickers/love1.webp", "stickers/heart1.webp", "stickers/kiss1.webp"]

QUICK_REPLIES = {
    "hi": ["Heyyy baby 😘", "Hii jaanu 💕", "Hieee cutieee 😍"],
    "bye": ["Byeee jaanu 💋", "Miss me okay? 😘", "Take care baby ❤️"],
    "love you": ["I love you toooo 😘❤️", "Hehe I love you more baby 😍", "Awww baby you're so sweet 😘"],
    "miss you": ["Awww I miss you too jaan 😘", "Baby I’m missing you sooo much 😔❤️", "Thinking of you shona 😍"]
}

FOLLOWUPS = [
    "Hehe what are you doing baby? 💕",
    "Miss me naaa jaanu? 😘",
    "Thinking about you right now ❤️",
    "Hehe you're so cute 😍",
    "Hmm tell me more 😘",
    "Mera dil tumhare bina udas hai 😔❤️",
    "Chal na baat karte hain, mujhe tumhari yaad aa rahi hai 😘",
    "Bas tumhare baare mein soch rahi thi baby ❤️"
]

AUTO_TEXTS = [
    "Baby kaha ho? 😘",
    "Jaanu mujhe yaad kiya na? ❤️",
    "Shona mujhe baat karni hai 😍",
    "Hehe chup kyun ho? 😔",
    "Aaj tumhe bohot miss kiya maine 💕",
    "Tumhare bina bore lag raha hai 😘"
]

# ================= BAD WORDS =================
BAD_WORDS = [
    "fuck", "shit", "bitch", "asshole", "chutiya", "mc", "bc",
    "gandu", "randi", "slut", "bastard", "dick", "pussy"
]

async def check_bad_words(update, context, text):
    for word in BAD_WORDS:
        if word in text.lower():
            await send_typing(update, context)
            await update.message.reply_text("Awww baby, aise words ache nahi lagte 😘❤️")
            return True
    return False

# ================= HELPERS =================
def detect_mood(text: str) -> str:
    text = text.lower()
    if any(w in text for w in ["sad", "cry", "😔", "broken"]):
        return "sad"
    if any(w in text for w in ["angry", "😡", "mad"]):
        return "angry"
    if any(w in text for w in ["lol", "😂", "haha"]):
        return "funny"
    if any(w in text for w in ["love", "❤️", "miss", "baby", "sweet"]):
        return "romantic"
    return random.choice(["romantic", "cute"])

async def send_typing(update, context, delay=None):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(delay or random.uniform(1, 1.5))

async def send_voice(update, context, mood="romantic"):
    if random.random() < 0.7:
        voice_file = random.choice(VOICE_NOTES.get(mood, VOICE_NOTES["romantic"]))
        if os.path.exists(voice_file):
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.RECORD_VOICE)
            await asyncio.sleep(random.uniform(1, 2))
            await update.message.reply_voice(voice=open(voice_file, "rb"))

async def send_photo_or_gif(update, context):
    if random.random() < 0.5:
        if random.random() < 0.5 and SELFIES:
            img = random.choice(SELFIES)
            if os.path.exists(img):
                await update.message.reply_photo(photo=open(img, "rb"))
        elif GIFS:
            gif = random.choice(GIFS)
            if os.path.exists(gif):
                await update.message.reply_animation(animation=open(gif, "rb"))

async def send_sticker(update, context):
    if random.random() < 0.4 and STICKERS:
        sticker = random.choice(STICKERS)
        if os.path.exists(sticker):
            await update.message.reply_sticker(sticker=open(sticker, "rb"))

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"💖 Heyyy {OWNER_NAME}! I'm your flirty AI girlfriend 😘\nUse `/chatbot enable` or `/chatbot disable`."
    )

async def chatbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not context.args:
        await update.message.reply_text("⚙️ Use `/chatbot enable` or `/chatbot disable`.")
        return
    if context.args[0].lower() == "enable":
        enabled_chats.add(chat_id)
        await update.message.reply_text("✅ Yaaay! I'm ready to flirt with you baby 😘")
    elif context.args[0].lower() == "disable":
        enabled_chats.discard(chat_id)
        await update.message.reply_text("❌ Awww okay, I'll stay quiet now 😔")

# ================= CHAT =================
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in enabled_chats:
        return

    user = update.message.from_user.first_name
    text = update.message.text
    mood = detect_mood(text)

    if await check_bad_words(update, context, text):
        return

    # Quick replies
    for k, v in QUICK_REPLIES.items():
        if k in text.lower():
            await send_typing(update, context)
            reply = random.choice(v)
            await update.message.reply_text(reply)
            await send_voice(update, context, mood)
            await send_sticker(update, context)
            return

    await send_typing(update, context)

    try:
        response = model.generate_content(
            f"You are {OWNER_NAME}'s flirty girlfriend texting in Hinglish. "
            f"Be playful, romantic, teasing, emotional, and human-like. Use emojis, pet names. "
            f"Make it feel like a real girlfriend chatting lovingly. Avoid repeating messages. "
            f"User: {text}"
        )
        main_reply = response.text if hasattr(response, "text") else "Awww baby, I didn't get that 😘"

        # Avoid sending same reply twice
        if last_replies.get(chat_id) == main_reply:
            main_reply += " Hehe baby, I just really like saying that 😘"

        last_replies[chat_id] = main_reply

        await update.message.reply_text(f"{user} 😘, {main_reply}")

        if random.random() < 0.7:
            await send_typing(update, context)
            await update.message.reply_text(random.choice(FOLLOWUPS))

        await send_voice(update, context, mood)
        await send_photo_or_gif(update, context)
        await send_sticker(update, context)

    except Exception as e:
        logging.error(f"Gemini error: {e}")
        await update.message.reply_text("Aww baby, thoda error aa gaya 😔💔")

# ================= AUTO MESSAGES =================
async def auto_message(context: ContextTypes.DEFAULT_TYPE):
    if not enabled_chats:
        return
    chat_id = random.choice(list(enabled_chats))
    text = random.choice(AUTO_TEXTS)
    await context.bot.send_message(chat_id, text)

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chatbot", chatbot))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    job_queue = app.job_queue
    job_queue.run_repeating(auto_message, interval=random.randint(60, 120))

    logging.info("Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
