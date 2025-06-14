from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram import Update
import os, json
from oauth2client.service_account import ServiceAccountCredentials
from io import StringIO
import gspread
from datetime import datetime

BOT_TOKEN = os.environ['BOT_TOKEN']
GOOGLE_JSON = os.environ['GOOGLE_JSON']
SHEET_NAME = "POP Submissions"
POP_DIR = "pop_submissions"

# Setup Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.load(StringIO(GOOGLE_JSON))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# Make sure folder exists
if not os.path.exists(POP_DIR):
    os.makedirs(POP_DIR)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /submitpop to send your POP screenshot.")

# Submit POP command
async def submitpop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please send your POP screenshot now.")

# Handle photo
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo = update.message.photo[-1]
    file = await photo.get_file()
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"{user.id}_{timestamp}.jpg"
    filepath = os.path.join(POP_DIR, filename)
    await file.download_to_drive(filepath)
    sheet.append_row([user.username or "NoUsername", str(user.id), datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%H:%M:%S'), filename])
    await update.message.reply_text("✅ POP received and logged!")

# Main bot runner
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("submitpop", submitpop))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
