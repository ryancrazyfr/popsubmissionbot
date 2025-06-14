from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
from io import StringIO

# === CONFIGURATION ===
BOT_TOKEN = '7854611527:AAHEP_ZsZ0cj3hOaPTiSz18hi9kYOotftDs'
CREDENTIALS_FILE = 'telegrampopbot-15680edde189.json'
SHEET_NAME = 'POP Submissions'
POP_DIR = 'pop_submissions'

# === SETUP GOOGLE SHEETS ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
google_json = os.environ['GOOGLE_JSON']
creds_dict = json.load(StringIO(google_json))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1  # Use first worksheet

# Make folder if it doesn't exist
if not os.path.exists(POP_DIR):
    os.makedirs(POP_DIR)

# === HANDLERS ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /submitpop to send your POP screenshot.")

async def submitpop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please send your screenshot now.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo = update.message.photo[-1]
    file = await photo.get_file()

    # Create filename and save
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"{user.id}_{timestamp}.jpg"
    filepath = os.path.join(POP_DIR, filename)
    await file.download_to_drive(filepath)

    # Add to Google Sheet
    date_str = datetime.now().strftime('%Y-%m-%d')
    time_str = datetime.now().strftime('%H:%M:%S')

    sheet.append_row([
        user.username or "NoUsername",
        str(user.id),
        date_str,
        time_str,
        filename
    ])

    await update.message.reply_text("✅ POP received and logged to Google Sheet!")

# === MAIN ===

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("submitpop", submitpop))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("🤖 POP bot running with Google Sheets logging...")
    app.run_polling()

if __name__ == "__main__":
    main()
