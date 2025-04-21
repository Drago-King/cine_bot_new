import os
import random
import time
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from keep_alive import keep_alive

TOKEN = os.environ["TOKEN"]
OWNER_ID = int(os.environ.get("OWNER_ID", 0))
PRIZE_LINK = "https://t.me/+MRzg7Ne77M8zYjk1"
VAULT = []

ALL_QUESTIONS = [
    {
        "question": "Valar Morghulis",
        "options": ["valar dohaeris", "dracarys", "winter is coming"],
        "answer": "valar dohaeris",
        "voice": "audio_clips/valar_dohaeris.ogg",
        "image": "audio_clips/valar_dohaeris.jpeg"
    },
    {
        "question": "Say my name.",
        "options": ["heisenberg", "walter white", "jesse pinkman"],
        "answer": "heisenberg",
        "voice": "audio_clips/heisenberg.ogg",
        "image": "audio_clips/heisenberg.jpeg"
    },
    {
        "question": "What was Maximus’ title before becoming a slave?",
        "options": ["General of the Roman Army", "Spaniard", "Caesar"],
        "answer": "General of the Roman Army",
        "voice": "audio_clips/maximus.ogg",
        "image": "audio_clips/maximus.jpeg"
    },
    {
        "question": "What is the first rule of F**** C***?",
        "options": ["you do not talk about f**** c***", "don’t mention the club", "fight only at night"],
        "answer": "you do not talk about f**** c***",
        "voice": "audio_clips/fight_club.ogg",
        "image": "audio_clips/fight_club.jpeg"
    },
    {
        "question": "Who watches the Watchmen?",
        "options": ["Who watches the Watchmen?", "No one", "We do"],
        "answer": "Who watches the Watchmen?",
        "voice": "audio_clips/watchmen.ogg",
        "image": "audio_clips/watchmen.jpeg"
    },
    {
        "question": "I'm gonna make him an offer he can't refuse.",
        "options": ["Vito Corleone", "Michael", "Sonny"],
        "answer": "Vito Corleone",
        "voice": "audio_clips/godfather.ogg",
        "image": "audio_clips/godfather.jpeg"
    }
]

STORY_CHAPTERS = [
    {
        "title": "The Dream of Electric Gods",
        "intro": "🌌 Neon tears fall under synthetic stars.",
        "voice": "audio_clips/chapter_blade_runner.ogg",
        "image": "audio_clips/chapter_blade_runner.jpeg"
    },
    {
        "title": "The Chaos Dilemma",
        "intro": "🃏 Justice rots in the hearts of men.",
        "voice": "audio_clips/chapter_dark_knight.ogg",
        "image": "audio_clips/chapter_dark_knight.jpeg"
    },
    {
        "title": "The Dream Spiral",
        "intro": "⏳ Gravity warps. Time loops.",
        "voice": "audio_clips/chapter_inception.ogg",
        "image": "audio_clips/chapter_inception.jpeg"
    },
    {
        "title": "The Red Pill Path",
        "intro": "🧠 You’re on the edge of reality.",
        "voice": "audio_clips/chapter_matrix.ogg",
        "image": "audio_clips/chapter_matrix.jpeg"
    },
    {
        "title": "The Man Who Burned the World",
        "intro": "☢️ Silence louder than any bomb.",
        "voice": "audio_clips/chapter_oppenheimer.ogg",
        "image": "audio_clips/chapter_oppenheimer.jpeg"
    },
    {
        "title": "The Cost of Kingship",
        "intro": "♟️ Crowned by blood, haunted by choices.",
        "voice": "audio_clips/chapter_sopranos.ogg",
        "image": "audio_clips/chapter_sopranos.jpeg"
    }
]

LORE_QUOTES = [
    "🎬 *A silent lens captures the loudest truths.*",
    "🎥 *Legends don’t fade—they are preserved in frames.*",
    "🕯️ *In shadows and whispers, stories awaken.*"
]

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("▶️ Start Quiz", callback_data="start_quiz")],
        [InlineKeyboardButton("🏛 Vault of Legends", callback_data="vault")],
        [InlineKeyboardButton("🎬 Story Mode", callback_data="story")],
        [InlineKeyboardButton("✨ Lore Drop", callback_data="lore")],
        [InlineKeyboardButton("📜 Rules", callback_data="rules")]
    ]
    update.message.reply_text("Welcome to the *Underrated Gems* world.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

def send_question(update: Update, context: CallbackContext):
    context.user_data["score"] = 0
    context.user_data["index"] = 0
    context.user_data["questions"] = random.sample(ALL_QUESTIONS, 4)
    ask_question(update, context)

def ask_question(update: Update, context: CallbackContext):
    try:
        idx = context.user_data["index"]
        if idx >= 4:
            score = context.user_data["score"]
            if score >= 3:
                username = update.effective_user.username or "Anonymous"
                VAULT.append(f"{username} ({update.effective_user.id})")
                update.callback_query.message.reply_text(f"🏆 Legendary! Claim your prize: {PRIZE_LINK}")
            else:
                update.callback_query.message.reply_text("☠️ You were close... but the vault remains shut.")
            return

        q = context.user_data["questions"][idx]
        context.user_data["correct"] = q["answer"]
        context.user_data["voice"] = q["voice"]
        context.user_data["image"] = q["image"]

        with open(q["image"], "rb") as img:
            buttons = [[InlineKeyboardButton(opt, callback_data=f"answer|{opt}")] for opt in q["options"]]
            update.callback_query.message.reply_photo(photo=img, caption=q["question"], reply_markup=InlineKeyboardMarkup(buttons))

    except Exception as e:
        update.callback_query.message.reply_text("⚠️ Error loading question.")
        print(f"[ERROR in ask_question] {e}")

def handle_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    chosen = query.data.split("|", 1)[1]
    correct = context.user_data.get("correct")
    voice = context.user_data.get("voice")

    if chosen.lower() == correct.lower():
        context.user_data["score"] += 1
        query.message.reply_text("✅ Correct.")
        try:
            with open(voice, "rb") as clip:
                query.message.reply_voice(voice=clip)
        except:
            query.message.reply_text("⚠️ Audio failed.")
    else:
        query.message.reply_text("❌ Incorrect.")

    context.user_data["index"] += 1
    time.sleep(1)
    ask_question(update, context)

def vault(update: Update, context: CallbackContext):
    if VAULT:
        legends = "\n".join(VAULT[-5:])
        update.callback_query.message.reply_text(f"🏛 *Vault of Legends:*\n{legends}", parse_mode="Markdown")
    else:
        update.callback_query.message.reply_text("🏛 The vault is empty.")

def lore(update: Update, context: CallbackContext):
    quote = random.choice(LORE_QUOTES)
    update.callback_query.message.reply_text(f"{quote}", parse_mode="Markdown")

def story(update: Update, context: CallbackContext):
    chapters = random.sample(STORY_CHAPTERS, 2)
    for scene in chapters:
        try:
            with open(scene["image"], "rb") as img:
                update.callback_query.message.reply_photo(photo=img, caption=f"*{scene['title']}*\n_{scene['intro']}_", parse_mode="Markdown")
            with open(scene["voice"], "rb") as clip:
                update.callback_query.message.reply_voice(voice=clip)
        except:
            continue

def rules(update: Update, context: CallbackContext):
    update.callback_query.message.reply_text("🎞 Answer 4 random cinematic questions.\n🎯 Score 3+ to unlock the Vault.\n☠️ One mistake too many... and you're out.")

def status(update: Update, context: CallbackContext):
    update.message.reply_text(f"✅ Bot is online.\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n🏆 Legends: {len(VAULT)}")

def handle_menu(update: Update, context: CallbackContext):
    data = update.callback_query.data
    if data == "start_quiz": send_question(update, context)
    elif data == "vault": vault(update, context)
    elif data == "story": story(update, context)
    elif data == "lore": lore(update, context)
    elif data == "rules": rules(update, context)

if __name__ == "__main__":
    keep_alive()
    updater = Updater(token=TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("ping", status))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CallbackQueryHandler(handle_answer, pattern=r"^answer\|"))
    dp.add_handler(CallbackQueryHandler(handle_menu))

    updater.start_polling()
    updater.idle()
