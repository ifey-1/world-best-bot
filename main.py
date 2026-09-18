import os, time, requests, threading
from flask import Flask

app = Flask(__name__)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHAT_ID")
BLACKLIST = ["0xb2000000000000000000000005b21d8272a739ea01"]

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHANNEL_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}, timeout=10)
    except Exception as e: print(e)

def get_gem(seen):
    try:
        # Better endpoint - gets REAL new pairs on Base
        r = requests.get("https://api.dexscreener.com/latest/dex/search/?q=base", timeout=15).json()
        pairs = r.get('pairs', [])[:80]
        for p in pairs:
            if p.get('chainId') != 'base': continue
            addr = p.get('baseToken', {}).get('address','').lower()
            if addr in seen: continue
            if addr in [b.lower() for b in BLACKLIST]: continue
            
            mcap = p.get('fdv',0) or 0
            liq = p.get('liquidity',{}).get('usd',0) or 0
            vol = p.get('volume',{}).get('h24',0) or 0
            sym = p.get('baseToken',{}).get('symbol','UNK')
            
            # V5 - LOOSE but SAFE - WILL CALL
            if not (3000 < mcap < 90000): continue
            if liq < 3500: continue  # Lowered from 12k to 3.5k = will call
            if vol < 150: continue   # Lowered from 1k to 150 = will call
            
            return {'symbol': sym.upper(), 'address': p['baseToken']['address'], 'mcap': mcap, 'liq': liq, 'vol': vol, 'pair': p['pairAddress']}
    except Exception as e:
        print(f"Scan err {e}")
    return None

def bot_loop():
    time.sleep(5)
    send_msg("🔥 V5 TURBO ONLINE - WILL CALL IN 90 SECONDS\n\nFilters: LIQ> $3.5k VOL> $150 (Loose)\nGuaranteed calls tonight for $10->$100 flip")
    seen=set([b.lower() for b in BLACKLIST])
    while True:
        try:
            time.sleep(90) # Call every 90 sec now
            gem = get_gem(seen)
            if gem:
                seen.add(gem['address'].lower())
                msg = f"""🚀 NEW GEM: ${gem['symbol']}

CA:
`{gem['address']}`

💰 MCAP: ${int(gem['mcap']):,}
💧 LIQ: ${int(gem['liq']):,}
📊 VOL: ${int(gem['vol']):,}

📈 https://dexscreener.com/base/{gem['pair']}

Fast flip - 2x sell half!"""
                send_msg(msg)
                print(f"Posted {gem['symbol']}")
            else:
                print("No gem, retrying...")
        except Exception as e:
            print(e)
            time.sleep(20)

@app.route('/')
def home(): return "V5 Running"
threading.Thread(target=bot_loop, daemon=True).start()
if __name__ == '__main__': app.run(host='0.0.0.0', port=10000)
