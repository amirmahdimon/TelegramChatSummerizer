import os
import sqlite3
from typing import List, Tuple
import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
# ---------------- CONFIG ----------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_PATH = "messages.db"

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("⚠️ لطفاً متغیرهای محیطی TELEGRAM_TOKEN و GEMINI_API_KEY را ست کنید.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-lite")

logging.basicConfig(level=logging.INFO)

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            username TEXT,
            text TEXT,
            message_id INTEGER,
            reply_to_message_id INTEGER
        )
        """
    )
    # Add columns if not exist
    try:
        c.execute("ALTER TABLE messages ADD COLUMN message_id INTEGER")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE messages ADD COLUMN reply_to_message_id INTEGER")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def save_message(chat_id: int, username: str, text: str, message_id: int, reply_to_message_id: int = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (chat_id, username, text, message_id, reply_to_message_id) VALUES (?, ?, ?, ?, ?)",
        (chat_id, username, text, message_id, reply_to_message_id),
    )
    conn.commit()
    conn.close()

def fetch_last_messages(chat_id: int, n: int) -> List[Tuple[str, str]]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT username, text FROM messages WHERE chat_id = ? ORDER BY id DESC LIMIT ?",
        (chat_id, n),
    )
    rows = c.fetchall()
    conn.close()
    return rows[::-1]

def format_messages(messages: List[Tuple[str, str]]) -> str:
    lines = []
    for username, text in messages:
        name = username or "ناشناس"
        lines.append(f"{name}: {text}")
    return "\n".join(lines)

# ---------------- GEMINI ----------------
async def summarize_with_gemini(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text.strip()

# ---------------- BOT HANDLERS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello guys 😈, I'm GhoncheSummerizer Bot!, Amir created me just for FARHAN.")

async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text:
        message_id = update.message.message_id
        reply_to = update.message.reply_to_message.message_id if update.message.reply_to_message else None
        save_message(
            update.message.chat.id,
            update.message.from_user.username or update.message.from_user.first_name,
            update.message.text,
            message_id,
            reply_to,
        )

async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Starting summarize command")
    n = 100
    if context.args:
        if context.args[0].isdigit():
            n = int(context.args[0])
            if n > 500:
                await update.message.reply_text("حداکثر ۵۰۰ پیام می‌تونی انتخاب کنی!")
                return
        else:
            await update.message.reply_text("عدد معتبر وارد کن!")
            return

    texts = fetch_last_messages(update.message.chat.id, n)
    print(f"Fetched {len(texts)} messages")
    if not texts:
        await update.message.reply_text("پیامی برای خلاصه‌سازی پیدا نشد 🤷‍♂️")
        return

    await update.message.reply_text("😈 دارم به سبک تحقیرآمیز خلاصه می‌کنم...")

    # Chunking for optimization
    chunk_size = 20
    chunks = [texts[i:i+chunk_size] for i in range(0, len(texts), chunk_size)]
    print(f"Split into {len(chunks)} chunks")
    all_summaries = []

    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}")
        combined = format_messages(chunk)

        prompt = f"""
        این متن‌ها مربوط به یک گروه تلگرام هستند.
        وظیفه‌ات اینه که به سبک طنز و انتقادی دوستانه برای هر کاربر یه توضیح مفصل‌تر از حرفاش بنویسی، با کمی مسخره کردن سبک.
        خلاصه‌ها رو کامل‌تر کن تا گم نشن، نه خیلی کوتاه.
        بدون توهین شدید یا آزاردهنده.

        خروجی باید به شکل زیر باشه:
        - username:
           😂 یک توضیح طنزآمیز مفصل از حرفاش

        متن پیام‌ها:
        {combined}
        """

        summary = await summarize_with_gemini(prompt)
        print(f"Chunk {i+1} summarized")
        all_summaries.append(summary)

    if len(all_summaries) == 1:
        final = all_summaries[0]
        print("Single chunk, using as final")
    else:
        print("Combining summaries")
        combined_summaries = "\n\n---\n\n".join(all_summaries)
        final_prompt = f"""
        این خلاصه‌های طنزآمیز از چانک‌های مختلف هستند.
        وظیفه‌ات اینه که همه رو ترکیب کنی و یه خلاصه نهایی طنزآمیز مفصل برای هر کاربر بسازم، بدون تکرار.
        سبک دوستانه و بدون توهین شدید.
        توضیح‌ها رو کامل‌تر کن مربوط به پیاماشون.
        ولی کمی اذیت بکن و تیکه بنداز

        خروجی به شکل:
        - username:
           😂 یک توضیح طنزآمیز مفصل کلی از حرفاش

        خلاصه‌ها:
        {combined_summaries}
        """
        final = await summarize_with_gemini(final_prompt)
        print("Final summary generated")

    # Find top 5 most replied messages
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    SELECT reply_to_message_id, COUNT(*) as reply_count
    FROM messages
    WHERE reply_to_message_id IS NOT NULL AND chat_id = ?
    GROUP BY reply_to_message_id
    ORDER BY reply_count DESC
    LIMIT 5
    """, (update.message.chat.id,))
    rows = c.fetchall()
    if rows:
        final += "\n\n**پیام‌های پرکاربرد (بیشترین ریپلای):**\n"
        for i, (original_id, count) in enumerate(rows, 1):
            c.execute("SELECT username, text FROM messages WHERE message_id = ? AND chat_id = ?", (original_id, update.message.chat.id))
            orig_row = c.fetchone()
            if orig_row:
                username, text = orig_row
                chat_id_str = str(update.message.chat.id)
                if chat_id_str.startswith('-100'):
                    link = f"https://t.me/c/{chat_id_str[4:]}/{original_id}"
                else:
                    link = f"Message ID: {original_id}"  # placeholder for public groups
                final += f"{i}. نام: {username}\nمتن: {text}\nتعداد ریپلای: {count}\nلینک: {link}\n\n"
    conn.close()

    await update.message.reply_text(final)

# ---------------- MAIN ----------------
def main():
    init_db()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("summary", summarize))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))

    app.run_polling()

if __name__ == "__main__":
    main()
