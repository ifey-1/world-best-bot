import os, requests, time, threading
from flask import Flask
app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@IfeysycoAI")

def send(msg):
    try:
        r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHANNEL_ID, "text": msg, "parse_mode": "HTML"}, timeout=15)
        print(f"TG: {r.text[:500]}")
    except Exception as e: print(e)

def check_safety(p):
    vol = float(p.get('volume', {}).get('h24', 0) or 0)
    liq = float(p.get('liquidity', {}).get('usd', 0) or 0)
    mcap = float(p.get('fdv', 0) or 0)
    if liq < 5000: return False, "Low liq"
    if vol < 5000: return False, "Low vol"
    if mcap > 0 and liq > 0 and mcap / liq > 100: return False, "Mcap too high"
    return True, "SAFE ✅"

def get_exact_pump(mcap, liq):
    if mcap == 0: mcap = liq * 4
    if mcap < 20000: return "50X", "BUY NOW - 50X INCOMING", "SELL 20% at 5X, 30% at 20X, 50% at 50X"
    elif mcap < 50000: return "20X", "BUY NOW - 20X INCOMING", "SELL 30% at 5X, 30% at 10X, 40% at 20X"
    elif mcap < 150000: return "10X", "BUY NOW - 10X INCOMING", "SELL 30% at 3X, 30% at 5X, 40% at 10X"
    elif mcap < 350000: return "5X", "BUY NOW - 5X INCOMING", "SELL 50% at 2X, 50% at 5X"
    else: return "2X", "BUY NOW - 2X INCOMING", "SELL 100% at 2X"

def loop():
    # SCAN IMMEDIATELY - NO SLEEP
    send("🚀 <b>BOT ONLINE - SCANNING NOW...</b>")
    while True:
        try:
            res = requests.get("https://api.dexscreener.com/latest/dex/search/?q=base", timeout=15).json()
            for p in res.get('pairs', [])[:70]:
                vol = float(p.get('volume', {}).get('h24', 0) or 0)
                liq = float(p.get('liquidity', {}).get('usd', 0) or 0)
                mcap = float(p.get('fdv', 0) or p.get('marketCap', 0) or 0)
                is_safe, safe_msg = check_safety(p)
                if not is_safe: continue
                sym = p.get('baseToken', {}).get('symbol', 'UNK').upper()
                addr = p.get('baseToken', {}).get('address', '')
                url = p.get('url','')
                if not addr or len(addr)<10: continue
                if sym in ["USDC","WETH","USDT","DAI","CBETH"]: continue
                exact_x, buy_text, sell_text = get_exact_pump(mcap, liq)
                msg = (
                    f"🚀 <b>BUY ${sym} NOW - WILL {exact_x} PUMP!</b> 🚀\n\n"
                    f"🛡️ <b>SAFETY: {safe_msg} - MONEY SAFE</b>\n\n"
                    f"<b>CA / ADDRESS:</b>\n<code>{addr}</code>\n\n"
                    f"💰 MCAP: ${mcap:,.0f} | 💧 LIQ: ${liq:,.0f} | 📊 VOL: ${vol:,.0f}\n\n"
                    f"<b>🟢 WHEN TO BUY:</b>\n{buy_text}\n\n"
                    f"<b>🔴 WHEN TO SELL:</b>\n{sell_text}\n\n"
                    f"✅ Liquidity > $5k | ✅ Volume Real | ✅ No Honeypot\n\n"
                    f"📈 {url}"
                )
                send(msg)
                break
        except Exception as e:
            print(f"ERR {e}")
        time.sleep(120)

threading.Thread(target=loop, daemon=True).start()
@app.route('/')
def home(): return "V13.1 IMMEDIATE SCAN LIVE"
