import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import subprocess

ACR_HOST = os.getenv("ACR_HOST")
ACR_ACCESS_KEY = os.getenv("ACR_ACCESS_KEY")
ACR_ACCESS_SECRET = os.getenv("ACR_ACCESS_SECRET")

def download_video(url):
    try:
        proc = subprocess.run(
            ["yt-dlp", url, "-o", "video.mp4"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if os.path.exists("video.mp4"):
            return "video.mp4"
        return None
    except:
        return None

def recognize_music(file_path):
    with open(file_path, "rb") as f:
        audio_data = f.read()

    data = {
        "access_key": ACR_ACCESS_KEY,
        "data_type": "audio",
        "signature_version": "1",
    }

    url = f"https://{ACR_HOST}/v1/identify"

    files = {
        "sample": ("sample", audio_data, "audio/mpeg")
    }

    r = requests.post(url, data=data, files=files)
    return r.json()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text and ("instagram.com" in text or "tiktok.com" in text):
        await update.message.reply_text("⏳ Videoni yuklab olyapman...")
        file = download_video(text)
        if file:
            await update.message.reply_video(video=open(file, "rb"))
            os.remove(file)
        else:
            await update.message.reply_text("❌ Videoni yuklab bo‘lmadi.")
        return

    if update.message.voice:
        await update.message.reply_text("🎵 Musiqa qidirilmoqda...")
        file = await update.message.voice.get_file()
        await file.download_to_drive("voice.ogg")
        result = recognize_music("voice.ogg")

        if "metadata" in result:
            track = result["metadata"]["music"][0]
            await update.message.reply_text(
                f"🎶 Topildi!

"
                f"📌 *{track['title']}*
"
                f"👤 {track['artists'][0]['name']}",
                parse_mode="Markdown",
            )
        else:
            await update.message.reply_text("❌ Musiqa topilmadi.")

        os.remove("voice.ogg")
        return

    await update.message.reply_text("🔗 Instagram/TikTok link yuboring yoki ovozli xabar yuboring.")

if __name__ == "__main__":
    token = os.getenv("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    print("Bot ishga tushdi...")
    app.run_polling()
