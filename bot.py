import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "7227747877:AAEFutKLq-eD0su9hnES09XSzQbr2X8YJOE"
API_URL = "http://103.87.67.78/signal"  # Ganti ke endpoint Flask kamu

async def cek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        r = requests.get(API_URL)
        if r.ok:
            msg = "Signal akan segera dikirimkan ke Telegram."
        else:
            msg = f"Terjadi kesalahan: {r.status_code} - {r.text}"
            with open("log.txt", "a") as log_file:
                log_file.write(f"{msg}\n")
    except Exception as e:
        msg = f"Gagal request: {e}"
    await update.message.reply_text(msg)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("cek", cek))  # Handler untuk /cek

if __name__ == "__main__":
    app.run_polling()
