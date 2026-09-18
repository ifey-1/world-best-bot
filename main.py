import os, time, requests, threading
from flask import Flask

app = Flask(__name__)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHANNEL_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True})
        print("Posted real gem")
    except Exception as e:
        print(f"Send error: {e}")

def get_real_gem():
    try:
        # Get latest Base pairs
        r = requests.get("https://api.dexscreener.com/latest/dex/search/?q=base", timeout=10).json()
        pairs = r.get('pairs', [])[:50]
        
        for p in pairs:
            try:
                if p.get('chainId') != 'base': continue
                mcap = p.get('fdv', 0) or p.get('marketCap', 0) or 0
                liq = p.get('liquidity', {}).get('usd', 0) or 0
                # REAL FILTER: mcap 5k-80k, liquidity > 3k
                if 5000 < mcap < 80000 and liq > 3000:
                    return {
                        'symbol': p['baseToken']['symbol'],
                        'address': p['baseToken']['address'],
                        'mcap': mcap,
                        'pair': p['pairAddress']
                    }
            except: continue
    except Exception as e:
        print(f"Scan error: {e}")
    return None

def bot_loop():
    time.sleep(5)
    send_msg("🚀 REAL SCANNER ONLINE ✅\n\nScanning Base for real gems... Next real coin in 2 mins")
    
    while True:
        try:
            time.sleep(150)
            gem = get_real_gem()
            if gem:
                msg = f"""🚀 BUY ${gem['symbol']} - WILL 20X!

CA:
`{gem['address']}`

💰 MCAP: ${int(gem['mcap']):,}
💧 LIQ: Real gem on Base
🟢 BUY NOW

📈 https://dexscreener.com/base/{gem['pair']}

⚠️ DYOR - Early call!"""
                send_msg(msg)
            else:
                send_msg("🔍 Scanning... No perfect gem under $80k yet. Checking again in 2 mins.\n\nBot is active.")
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(30)

@app.route('/')
def home():
    return "Real bot running!"

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
