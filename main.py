import os, time, threading, requests
from flask import Flask

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@IfeysycoAI")
app = Flask(__name__)

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": CHANNEL_ID, "text": text}, timeout=10)
        print(f"Sent: {r.status_code} - {text[:30]}")
    except Exception as e:
        print(f"Error: {e}")

def get_pumps():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=price_change_percentage_1h_desc&per_page=20&page=1&price_change_percentage=1h,24h"
        data = requests.get(url, timeout=20).json()
        # Lowered to 3% so you ALWAYS get alerts
        pumps = [c for c in data if c.get('price_change_percentage_1h_in_currency', 0) and c.get('price_change_percentage_1h_in_currency') > 3]
        if not pumps:
            # If no pump, send top mover anyway as heartbeat
            pumps = data[:1]
        return pumps[:3]
    except Exception as e:
        print(f"get_pumps error: {e}")
        return []

def scanner_loop():
    send_telegram("🚀 WORLD BEST BOT LIVE\n✅ Fixed & Awake!\nScanning for pumps every 3 mins...")
    time.sleep(10)
    counter = 0
    while True:
        try:
            counter += 1
            pumps = get_pumps()
            if pumps:
                for coin in pumps:
                    change_1h = coin.get('price_change_percentage_1h_in_currency', 0)
                    price = coin.get('current_price', 0)
                    msg = f"🚀 PUMP ALERT: ${coin['symbol'].upper()}\n💰 Price: ${price}\n📈 1h: +{change_1h:.2f}%\n\n⚡ Entry NOW!"
                    send_telegram(msg)
                    time.sleep(2)
            else:
                send_telegram(f"🔍 SCAN {counter}: Market quiet, no 3%+ pump. Bot alive & scanning... Next scan in 3 mins.")
            time.sleep(180)  # 3 mins
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(30)

@app.route('/')
def home():
    return "BOT LIVE - Scanning"

threading.Thread(target=scanner_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
