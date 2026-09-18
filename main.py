import os, time, requests, threading
from flask import Flask
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHANNEL_ID, "text": text, "parse_mode": "Markdown"})
        print(f"Posted: {text[:30]}")
    except Exception as e:
        print(f"Send error: {e}")

def bot_loop():
    time.sleep(5)
    send_msg("🚀 BOT ONLINE - READY ✅\n\nNext gem in 2 mins...")
    print("Bot started!")
    
    count = 1
    while True:
        try:
            time.sleep(150) # 2.5 mins
            # FOR TESTING - we post a test gem so you see it working
            msg = f"""🚀 BUY $TEST{count} - WILL 20X!

CA:
0x{count}1234567890123456789012345678901234abcd

💰 MCAP: $23,000
🟢 BUY NOW - Early gem!

📈 https://dexscreener.com/base/0x123

Next call in 2.5 mins..."""
            send_msg(msg)
            count += 1
            print(f"Posted call #{count}")
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(30)

@app.route('/')
def home():
    return "Bot is running!"

# Start bot in background
threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
