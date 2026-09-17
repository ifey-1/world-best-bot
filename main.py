import os, time, threading, requests
from flask import Flask

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8483568575:AAHBeA4yW0C4Zqt8z6g4JfJq7wQ8s8f8s8f")
CHANNEL_ID = "@IfeysycoAI"
app = Flask(__name__)

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHANNEL_ID, "text": text, "parse_mode": "Markdown"}, timeout=15)
        print("Sent")
    except Exception as e:
        print(e)

def get_pumps():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=volume_desc&per_page=25&page=1&price_change_percentage=1h,24h"
        data = requests.get(url, timeout=20).json()
        pumps = [c for c in data if (c.get('price_change_percentage_1h_in_currency',0) or 0) > 1.5]
        return pumps[:3]
    except:
        return []

def scanner_loop():
    send_telegram("🚀 *WORLD BEST BOT LIVE*\nScanning for pumps every 3 mins...")
    time.sleep(10)
    while True:
        for coin in get_pumps():
            msg = f"🔥 *PUMP ALERT: ${coin['symbol'].upper()}*\n\n{coin['name']}\nPrice: ${coin['current_price']}\n1H: +{(coin.get('price_change_percentage_1h_in_currency',0) or 0):.2f}%\n\n📈 Early entry - 2X potential"
            send_telegram(msg)
            time.sleep(2)
        time.sleep(180)

@app.route('/')
def home():
    return "BOT LIVE"

threading.Thread(target=scanner_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
