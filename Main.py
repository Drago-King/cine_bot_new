import os
import random
import time
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from keep_alive import keep_alive

TOKEN = os.environ["TOKEN"]
OWNER_ID = os.environ.get("OWNER_ID", "2136911686")
PRIZE_LINK = "https://t.me/+MRzg7Ne77M8zYjk1"
VAULT = []

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
            "always fight there",
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

CORRECT_LINES = [
    "✅ Correct! The gods of cinema nod in approval.",
    "✅ Flawless. You walk among legends.",
    "✅ You've earned your place in the Vault."
]

WRONG_LINES = [
    "❌ Not worthy... yet.",
    "❌ You fall short of cinematic greatness.",
    "❌ The Vault remains locked to you."
]

LORE_QUOTES = [
    "A silent lens captures the loudest truths.",
    "Legends don’t fade—they are preserved in frames.",
    "In shadows and whispers, stories awaken.",
    "A director's cut never lies.",
    "Some scripts are written in blood, others in legacy."
]

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🎯 Start Quiz", callback_data="start_quiz")],
        [InlineKeyboardButton("🏆 Vault of Legends", callback_data="vault")],
        [InlineKeyboardButton("🎬 Cinematic Story Mode", callback_data="story")],
        [InlineKeyboardButton("📜 Lore Drop", callback_data="lore")],
        [InlineKeyboardButton("❓ Rules", callback_data="rules")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Welcome to *Twist & Terror* — the cinematic challenge begins.", reply_markup=reply_markup, parse_mode='Markdown')

def send_question(update: Update, context: CallbackContext):
    context.user_data["score"] = 0
    context.user_data["index"] = 0
    context.user_data["questions"] = random.sample(ALL_QUESTIONS, 3)
    ask_question(update, context)

def ask_question(update: Update, context: CallbackContext):
    idx = context.user_data["index"]
    if idx >= len(context.user_data["questions"]):
        score = context.user_data["score"]
        if score == 3:
            username = update.effective_user.username or "Anonymous"
            VAULT.append(username)
            update.callback_query.message.reply_text(f"🏆 *Legendary!* Claim your prize: {PRIZE_LINK}", parse_mode='Markdown')
        else:
            update.callback_query.message.reply_text("🚫 You were close... but the Vault remains sealed.")
        return
    q = context.user_data["questions"][idx]
    context.user_data["correct"] = q["answer"]
    context.user_data["voice"] = q["voice"]
    buttons = [[InlineKeyboardButton(opt, callback_data=f"answer|{opt}")] for opt in q["options"]]
    reply_markup = InlineKeyboardMarkup(buttons)
    update.callback_query.message.reply_text(f"*{q['question']}*", reply_markup=reply_markup, parse_mode="Markdown")

def handle_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    chosen = query.data.split("|", 1)[1]
    correct = context.user_data["correct"]
    voice_path = context.user_data["voice"]
    if chosen.lower() == correct.lower():
        context.user_data["score"] += 1
        query.message.reply_text(random.choice(CORRECT_LINES))
        try:
            query.message.bot.send_voice(chat_id=query.message.chat_id, voice=open(voice_path, "rb"))
        except:
            query.message.reply_text("⚠️ Voice clip failed to load.")
    else:
        query.message.reply_text(random.choice(WRONG_LINES))
    context.user_data["index"] += 1
    time.sleep(1)
    ask_question(update, context)

def lore(update: Update, context: CallbackContext):
    quote = random.choice(LORE_QUOTES)
    update.callback_query.message.reply_text(f"✨ *Lore Drop:*\n_{quote}_", parse_mode="Markdown")

def vault(update: Update, context: CallbackContext):
    if VAULT:
        legends = "\n".join([f"🔥 {u}" for u in VAULT[-5:]])
        update.callback_query.message.reply_text(f"🏆 *Vault of Legends:*\n{legends}", parse_mode="Markdown")
    else:
        update.callback_query.message.reply_text("🚪 The Vault is empty. Be the first to enter glory.")

def story(update: Update, context: CallbackContext):
    clips = random.sample([q["voice"] for q in ALL_QUESTIONS], 2)
    update.callback_query.message.reply_text("🎬 *Cinematic Story Mode Activated...*", parse_mode="Markdown")
    for clip in clips:
        try:
            update.callback_query.message.reply_voice(voice=open(clip, "rb"))
        except:
            continue

def rules(update: Update, context: CallbackContext):
    update.callback_query.message.reply_text(
        "📜 *How to Play:*\n"
        "• You get 3 random cinematic questions.\n"
        "• Score all 3 to enter the *Vault of Legends*.\n"
        "• One mistake... and you're out.",
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
