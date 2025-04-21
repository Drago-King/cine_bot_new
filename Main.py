import os
import random
import time
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from keep_alive import keep_alive

# Load environment variables
TOKEN = os.environ["TOKEN"]
OWNER_ID = os.environ.get("OWNER_ID", "2136911686")
PRIZE_LINK = "https://t.me/+MRzg7Ne77M8zYjk1"
VAULT = []

# Cinematic Story Chapters
STORY_CHAPTERS = [
    {
        "title": "The Dream of Electric Gods",
        "intro": "🌌 Neon tears fall under synthetic stars. Welcome to a memory you never lived.",
        "voice": "audio_clips/chapter_blade_runner.ogg"
    },
    {
        "title": "The Chaos Dilemma",
        "intro": "🃏 Justice rots in the hearts of men. The villain within you whispers louder.",
        "voice": "audio_clips/chapter_dark_knight.ogg"
    },
    {
        "title": "The Dream Spiral",
        "intro": "⏳ Gravity warps. Reality bends. Time loops inside your thoughts.",
        "voice": "audio_clips/chapter_inception.ogg"
    },
    {
        "title": "The Red Pill Path",
        "intro": "🧠 You’re on the edge of reality. One step forward, and you’ll never go back.",
        "voice": "audio_clips/chapter_matrix.ogg"
    },
    {
        "title": "The Man Who Burned the World",
        "intro": "☢️ Silence louder than any bomb. The world cracked open with one whisper.",
        "voice": "audio_clips/chapter_oppenheimer.ogg"
    },
    {
        "title": "The Cost of Kingship",
        "intro": "♟️ Crowned by blood, haunted by choices. Family. Loyalty. Regret.",
        "voice": "audio_clips/chapter_sopranos.ogg"
    }
]

# Quiz Questions
ALL_QUESTIONS = [
    {
        "question": "Valar Morghulis",
        "options": ["valar dohaeris", "dracarys", "winter is coming"],
        "answer": "valar dohaeris",
        "voice": "audio_clips/valar_dohaeris.ogg"
    },
    {
        "question": "Say my name",
        "options": ["heisenberg", "walter white", "jesse pinkman"],
        "answer": "heisenberg",
        "voice": "audio_clips/heisenberg.ogg"
    },
    {
        "question": "What was Maximus' title before becoming a slave?",
        "options": ["General of the Roman Army", "Spaniard", "Caesar"],
        "answer": "General of the Roman Army",
        "voice": "audio_clips/maximus.ogg"
    },
    {
        "question": "What is the first rule of F**** C***?",
        "options": [
            "you do not talk about it",
            "always stay calm",
            "fight only at night"
        ],
        "answer": "you do not talk about it",
        "voice": "audio_clips/fight_club.ogg"
    },
    {
        "question": "Who watches the Watchmen?",
        "options": [
            "Who watches the Watchmen?",
            "No one",
            "We do"
        ],
        "answer": "Who watches the Watchmen?",
        "voice": "audio_clips/watchmen.ogg"
    }
]

# Lore Quotes
LORE_QUOTES = [
    "🎬 *A silent lens captures the loudest truths.*",
    "🎥 *Legends don’t fade—they are preserved in frames.*",
    "🕯️ *In shadows and whispers, stories awaken.*",
    "✂️ *A director's cut never lies.*",
    "🩸 *Some scripts are written in blood, others in legacy.*"
]

# Start Menu
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🎯 Start Quiz", callback_data="start_quiz")],
        [InlineKeyboardButton("🏛️ Vault of Legends", callback_data="vault")],
        [InlineKeyboardButton("🎬 Story Mode", callback_data="story")],
        [InlineKeyboardButton("📜 Lore Drop", callback_data="lore")],
        [InlineKeyboardButton("❓ Rules", callback_data="rules")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Welcome to the gates of *Underrated Gems World*.", reply_markup=reply_markup, parse_mode='Markdown')

def send_question(update: Update, context: CallbackContext):
    context.user_data["score"] = 0
    context.user_data["index"] = 0
    context.user_data["questions"] = random.sample(ALL_QUESTIONS, 3)
    ask_question(update, context)

def ask_question(update: Update, context: CallbackContext):
    try:
        idx = context.user_data["index"]
        if idx >= len(context.user_data["questions"]):
            score = context.user_data["score"]
            if score == 3:
                VAULT.append(update.effective_user.username)
                update.callback_query.message.reply_text(f"Legendary! Claim your prize: {PRIZE_LINK}")
            else:
                update.callback_query.message.reply_text("You were close... but the vault remains shut.")
            return

        q = context.user_data["questions"][idx]
        context.user_data["correct"] = q["answer"]
        context.user_data["voice"] = q["voice"]
        buttons = [[InlineKeyboardButton(opt, callback_data=f"answer|{opt}")] for opt in q["options"]]
        reply_markup = InlineKeyboardMarkup(buttons)

        update.callback_query.message.reply_text(q["question"], reply_markup=reply_markup)

    except Exception as e:
        print(f"[ERROR in ask_question] {e}")
        update.callback_query.message.reply_text("Something went wrong with this question.")

def handle_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    chosen = query.data.split("|", 1)[1]
    correct = context.user_data["correct"]
    voice_path = context.user_data["voice"]

    if chosen.lower() == correct.lower():
        context.user_data["score"] += 1
        query.message.reply_text("✅ Correct. The gods of cinema nod.")
        try:
            query.message.bot.send_voice(chat_id=query.message.chat_id, voice=open(voice_path, "rb"))
        except:
            query.message.reply_text("⚠️ Voice clip failed to load.")
    else:
        query.message.reply_text("❌ Not worthy yet...")

    context.user_data["index"] += 1
    time.sleep(1)
    ask_question(update, context)

def story(update: Update, context: CallbackContext):
    chapter = random.choice(STORY_CHAPTERS)
    update.callback_query.message.reply_text(f"*{chapter['title']}*\n_{chapter['intro']}_", parse_mode="Markdown")
    try:
        update.callback_query.message.reply_voice(voice=open(chapter["voice"], "rb"))
    except:
        update.callback_query.message.reply_text("⚠️ Audio not available.")

def lore(update: Update, context: CallbackContext):
    quote = random.choice(LORE_QUOTES)
    update.callback_query.message.reply_text(f"{quote}", parse_mode="Markdown")

def vault(update: Update, context: CallbackContext):
    if VAULT:
        legends = "\n".join([f"🔥 {u}" for u in VAULT[-10:]])
        update.callback_query.message.reply_text(f"🏛️ *Vault of Legends:*\n{legends}", parse_mode="Markdown")
    else:
        update.callback_query.message.reply_text("🕳️ The Vault is empty. Be the first to enter glory.")

def rules(update: Update, context: CallbackContext):
    update.callback_query.message.reply_text(
        "📜 *How to Play:*\n"
        "• Answer 3 random cinematic questions.\n"
        "• Score all to unlock the *Vault of Legends*.\n"
        "• One mistake and you're out.",
        parse_mode="Markdown"
    )

def status(update: Update, context: CallbackContext):
    total = len(VAULT)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update.message.reply_text(
        f"🛰️ Bot is *alive*.\n⏱ Time: `{now}`\n🏆 Legends in Vault: {total}",
        parse_mode="Markdown"
    )

def handle_menu(update: Update, context: CallbackContext):
    data = update.callback_query.data
    if data == "start_quiz":
        send_question(update, context)
    elif data == "vault":
        vault(update, context)
    elif data == "story":
        story(update, context)
    elif data == "lore":
        lore(update, context)
    elif data == "rules":
        rules(update, context)

if __name__ == "__main__":
    keep_alive()
    updater = Updater(token=TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("ping", status))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CallbackQueryHandler(handle_answer, pattern="^answer\\|"))
    dp.add_handler(CallbackQueryHandler(handle_menu, pattern="^(start_quiz|vault|story|lore|rules)$"))

    updater.start_polling()
    updater.idle()
