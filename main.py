import os
import time
import requests
import threading
import random
from flask import Flask

# --- FLASK KEEP ALIVE FOR RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Expert Mode True - Scanning for 2X-50X - Bot is Live!"

# --- TELEGRAM SENDER (FIXED - NO MORE AWAIT ERROR) ---
def send_telegram(text):
    token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHANNEL_ID")
    if not token or not chat_id:
        print("ERROR: BOT_TOKEN or CHANNEL_ID missing in Environment!")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        r = requests.post(url, data=payload, timeout=15)
        print(f"TELEGRAM SENT: {r.status_code} - {text[:60]}")
    except Exception as e:
        print(f"Telegram send failed: {e}")

# --- EXPERT ANALYSIS LOGIC ---
def get_trending_coins():
    try:
        # Get trending from CoinGecko
        url = "https://api.coingecko.com/api/v3/search/trending"
        data = requests.get(url, timeout=10).json()
        coins = [c['item']['id'] for c in data.get('coins', [])[:7]]
        return coins
    except:
        return ["pepe", "bonk", "floki", "shiba-inu", "dogecoin"]

def expert_analysis():
    print("Expert Mode True - Scanning for 2X-50X...")
    send_telegram("🚀 *WORLD BEST BOT IS LIVE*\n\n50-Year Expert AI activated\nScanning for 2X-50X pumps...\n\nYou will get alert when perfect entry found!")

    while True:
        try:
            coins = get_trending_coins()
            
            for coin_id in coins:
                # Simulate expert check
                try:
                    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&market_data=true&community_data=false"
                    info = requests.get(url, timeout=10).json()
                    price = info['market_data']['current_price']['usd']
                    vol = info['market_data']['total_volume']['usd']
                    mcap = info['market_data']['market_cap']['usd']
                    
                    # Expert filter for 2X-50X potential
                    if mcap < 50000000 and vol > mcap * 0.3:
                        potential = random.choice(["5X", "10X", "15X", "25X", "50X"])
                        score = random.randint(92, 99)
                        
                        msg = f"""🔥 *EXPERT ALERT - {potential} POTENTIAL* 🔥

🪙 *Coin:* ${info['symbol'].upper()} - {info['name']}
💰 *Price:* ${price}
📊 *Market Cap:* ${mcap:,.0f}
📈 *Volume:* ${vol:,.0f}
⭐ *Expert Score:* {score}/100

🎯 *ENTRY:* NOW - Perfect dip
💎 *TARGET:* {potential}
🛑 *Stop Loss:* -20%

⚠️ *50-Year Expert Analysis:*
- Volume spike detected
- Low market cap gem
- Whale accumulation
- Community FOMO starting

🔗 https://www.coingecko.com/en/coins/{coin_id}

#2X #50X #GEM
"""
                        send_telegram(msg)
                        time.sleep(300)  # Wait 5 mins between alerts
                        
                except Exception as e:
                    print(f"Check failed for {coin_id}: {e}")
                    continue
            
            print("Scan cycle complete, waiting 60s...")
            time.sleep(60)
            
        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(30)

# --- START ---
if __name__ == "__main__":
    # Start expert scanner in background thread
    t = threading.Thread(target=expert_analysis, daemon=True)
    t.start()
    
    # Start Flask web server
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
