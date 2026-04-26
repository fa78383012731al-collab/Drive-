import os
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, Filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, use_context=True)

# رفع الملف إلى Google Drive
def upload_to_drive(file_url, file_name):
    file_data = requests.get(file_url).content

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    files = {
        'data': ('metadata', '{"name": "' + file_name + '"}', 'application/json'),
        'file': (file_name, file_data)
    }

    response = requests.post(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
        headers=headers,
        files=files
    )

    return response.json()

# استقبال الملفات
def handle_file(update, context):
    file = update.message.document
    if not file:
        update.message.reply_text("أرسل ملف")
        return

    file_obj = context.bot.get_file(file.file_id)
    file_url = file_obj.file_path

    update.message.reply_text("جاري الرفع...")

    result = upload_to_drive(file_url, file.file_name)

    if "id" in result:
        link = f"https://drive.google.com/file/d/{result['id']}/view"
        update.message.reply_text(f"تم الرفع ✅\n{link}")
    else:
        update.message.reply_text("فشل الرفع ❌")

dispatcher.add_handler(MessageHandler(Filters.document, handle_file))

# webhook endpoint
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def home():
    return "Bot is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
