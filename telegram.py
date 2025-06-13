import requests
import traceback

bot_token = '7227747877:AAEFutKLq-eD0su9hnES09XSzQbr2X8YJOE'
chat_id = '-4837667613'

def send_telegram_message(message, chat_id=chat_id):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    try:
        data = {
            'chat_id': chat_id,
            'text': format_telegram_message(message),
            'parse_mode': 'HTML'
        }
        # print(data)
        response = requests.post(url, data=data)
        if not response.ok:
            raise Exception(f"Failed to send message: {response.status_code} - {response.text}")

        return response.json()
    except Exception as e:
        with open("log.txt", "a") as f:
            f.write(f"Error sending Telegram message: {e}\n")
            f.write(traceback.format_exc())
            f.write("URL:\n")
            f.write(f"{url}\n")
        return {"ok": False, "error": str(e)}

def format_telegram_message(saham):
    pesan = f"📈 <b>Kode:</b> <b>{saham['ticker']}</b> \n"
    pesan += f"🗓️ <b>Tanggal:</b> {saham['date']}\n"
    pesan += f"💵 <b>Open:</b> {saham['open_price']}\n"
    pesan += f"💰 <b>Close:</b> {saham['close_price']}\n"
    pesan += f"🎯 <b>Entry:</b> {saham['entry_price']} | <b>Target:</b> {saham['target_price']} | <b>Cutloss:</b> {saham['cut_loss']}\n"
    pesan += f"⭐ <b>Score:</b> {saham['score']}\n"
    pesan += "\n<b>Alasan Sinyal:</b>\n"
    for i, reason in enumerate(saham['reasons'], 1):
        pesan += f"{i}. {reason}\n"

    if saham.get('news'):
        pesan += "\n📰 <b>Berita Terkait:</b>\n"
        for berita in saham['news']:
            pesan += f"- <a href=\"{berita['link']}\">{berita['title']}</a>\n"

    return pesan
