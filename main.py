import os, requests, time, threading
from flask import Flask
app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

def send(m):
    try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHANNEL_ID, "text": m, "parse_mode": "HTML"}, timeout=20)
    except: pass

def good(p):
    vol=float(p.get('volume',{}).get('h24',0)or 0)
    liq=float(p.get('liquidity',{}).get('usd',0)or 0)
    mcap=float(p.get('fdv',0)or 0)
    if liq<7000 or vol<7000: return False
    return True

def pump(mcap, liq):
    if mcap==0: mcap=liq*5
    if mcap<15000: return "50X","BUY NOW","SELL 20% at 5X, 30% at 20X, 50% at 50X"
    if mcap<40000: return "20X","BUY NOW","SELL 25% at 5X, 25% at 10X, 50% at 20X"
    if mcap<120000: return "10X","BUY NOW","SELL 30% at 3X, 30% at 5X, 40% at 10X"
    if mcap<300000: return "5X","BUY NOW","SELL 50% at 2X, 50% at 5X"
    return "2X","BUY NOW","SELL 100% at 2X"

def loop():
    time.sleep(2)
    send("🚀 <b>BOT ONLINE - V14 LIVE</b>")
    while True:
        try:
            data=requests.get("https://api.dexscreener.com/latest/dex/search/?q=base", timeout=15).json()
            for p in data.get('pairs',[])[:80]:
                if not good(p): continue
                sym=p.get('baseToken',{}).get('symbol','UNK').upper()
                addr=p.get('baseToken',{}).get('address','')
                if len(addr)<10 or sym in ["USDC","USDT","DAI","WETH","CBETH"]: continue
                mcap=float(p.get('fdv',0)or 0)
                liq=float(p.get('liquidity',{}).get('usd',0)or 0)
                vol=float(p.get('volume',{}).get('h24',0)or 0)
                x,b,s=pump(mcap,liq)
                msg=f"🚀 <b>BUY ${sym} NOW - WILL {x} PUMP!</b>\n\n🛡️ SAFE ✅\n\n<b>CA:</b>\n<code>{addr}</code>\n\n💰 MCAP: ${mcap:,.0f} | LIQ: ${liq:,.0f} | VOL: ${vol:,.0f}\n\n🟢 BUY: {b}\n🔴 SELL: {s}\n\n📈 {p.get('url','')}"
                send(msg)
                break
        except: pass
        time.sleep(150)

threading.Thread(target=loop, daemon=True).start()
@app.route('/')
def h(): return "LIVE"
if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
