import os, requests, time, threading
from flask import Flask
from datetime import datetime
app = Flask(__name__)

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()
CHANNEL_ID = (os.getenv("CHANNEL_ID") or "@IfeysycoAI").strip()

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHANNEL_ID, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=15)
        print(f"TG: {r.text[:200]}")
    except Exception as e: print(e)

def make_call(p):
    sym = p.get('baseToken',{}).get('symbol','UNK')
    name = p.get('baseToken',{}).get('name','Unknown')
    addr = p.get('baseToken',{}).get('address','')
    price = p.get('priceUsd','0')
    liq = float(p.get('liquidity',{}).get('usd',0) or 0)
    vol = float(p.get('volume',{}).get('h24',0) or 0)
    mcap = float(p.get('fdv',0) or 0)
    chain = p.get('chainId','base').upper()
    potential = "50x" if mcap < 100000 else "20x" if mcap < 500000 else "5x-10x" if mcap < 2000000 else "2x-5x"
    msg = f"""🚀 <b>NEW GEM CALL - {potential} POTENTIAL</b> 🚀

💰 <b>${sym} | {name}</b>
🌐 {chain} | 💵 ${price}
💧 Liq ${liq:,.0f} | Vol ${vol:,.0f}
🏦 MCap ${mcap:,.0f}

📋 <b>CA:</b>
<code>{addr}</code>

📊 <b>PLAN:</b>
✅ BUY NOW - Early
🎯 30% at 2x, 30% at 5x, 20% at 10x, 20% to {potential}
🛑 SL -40% if liq < $5k

🔗 {p.get('url','')}
⏰ {datetime.now().strftime('%H:%M WAT')}"""
    send(msg)

def loop():
    time.sleep(5)
    send(f"🚀 <b>V9 FINAL ONLINE ✅</b>\nBot fixed - will post calls with CA now!")
    while True:
        try:
            data = requests.get("https://api.dexscreener.com/latest/dex/search/?q=base", timeout=15).json()
            for p in data.get('pairs',[])[:15]:
                vol = float(p.get('volume',{}).get('h24',0) or 0)
                liq = float(p.get('liquidity',{}).get('usd',0) or 0)
                if vol >= 150000 and liq >= 5000:
                    make_call(p)
                    break
            time.sleep(600)
        except: time.sleep(60)

threading.Thread(target=loop, daemon=True).start()

@app.route('/')
def home(): return "LIVE"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT",10000)))
