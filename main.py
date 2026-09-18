import os, time, requests, threading
from flask import Flask
from datetime import datetime

app = Flask(__name__)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHANNEL_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}, timeout=15)
    except: pass

def get_gem(seen):
    try:
        # Get NEWEST pools on Base - sorted by creation time
        r = requests.get("https://api.dexscreener.com/latest/dex/search/?q=base", timeout=15).json()
        pairs = r.get('pairs', [])
        # Sort by newest first
        pairs = sorted(pairs, key=lambda x: x.get('pairCreatedAt',0) or 0, reverse=True)[:150]
        
        for p in pairs:
            if p.get('chainId') != 'base': continue
            addr = p.get('baseToken',{}).get('address','').lower()
            if not addr or addr in seen: continue
            
            mcap = p.get('fdv',0) or 0
            liq = p.get('liquidity',{}).get('usd',0) or 0
            
            # V7 ULTRA LOOSE - WILL CALL
            if not (500 < mcap < 250000): continue
            if liq < 1000: continue  # Super low to guarantee call
            
            return {
                'symbol': p['baseToken']['symbol'].upper(),
                'address': p['baseToken']['address'],
                'mcap': mcap, 'liq': liq,
                'vol': p.get('volume',{}).get('h24',0),
                'pair': p.get('pairAddress','')
            }
    except Exception as e:
        print(e)
    return None

def bot_loop():
    time.sleep(3)
    send_msg("🔥 V7 ULTRA ONLINE - Real new scan - First gem in 30s!")
    seen=set()
    first=True
    while True:
        try:
            time.sleep(30 if first else 60)
            first=False
            gem = get_gem(seen)
            if gem:
                seen.add(gem['address'].lower())
                if len(seen)>300: seen.clear()
                msg = f"""🚀 NEW GEM: ${gem['symbol']}

CA:
`{gem['address']}`

💰 MCAP: ${int(gem['mcap']):,}
💧 LIQ: ${int(gem['liq']):,}
📊 VOL: ${int(gem['vol']):,}

📈 https://dexscreener.com/base/{gem['pair']}

— FLIP PLAN $10->$100 —
✅ BUY if <30min old & chart flat
❌ SKIP if already 5x

💸 SELL:
2x = Sell 50% (secure)
3x = Sell 80% (profit)
Hold 20% moon"""
                send_msg(msg)
            # Removed the spam "no safe gem" message - it will just stay quiet until it finds one
        except Exception as e:
            print(e)
            time.sleep(10)

@app.route('/')
def home(): return "V7 Running"
threading.Thread(target=bot_loop, daemon=True).start()
if __name__ == '__main__': app.run(host='0.0.0.0', port=10000)
