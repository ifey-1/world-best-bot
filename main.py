import os, time, requests, threading
from flask import Flask

app = Flask(__name__)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHAT_ID")

BLACKLIST_ADDR = [
"0xb2000000000000000000000005b21d8272a739ea01",
"0x2a7dc23e29acc92ac6decf909af66a247c76076e",
"0xf1b4ddf712e108cf43711b1c39f2fddb0d5ce243"
]
BLACKLIST_SYMBOL = ["BASE","WETH","USDC","USDT","WBASE"]

def send_msg(t):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id":CHANNEL_ID,"text":t,"parse_mode":"Markdown","disable_web_page_preview":True},timeout=10)
    except: pass

def get_gem(seen):
    try:
        r = requests.get("https://api.dexscreener.com/latest/dex/search/?q=base",timeout=15).json()
        pairs = sorted(r.get('pairs',[]), key=lambda x: x.get('pairCreatedAt',0) or 0, reverse=True)[:150]
        for p in pairs:
            if p.get('chainId')!='base': continue
            sym = p.get('baseToken',{}).get('symbol','').upper()
            addr = p.get('baseToken',{}).get('address','').lower()
            if not addr or addr in seen: continue
            if addr in [b.lower() for b in BLACKLIST_ADDR]: continue
            if sym in BLACKLIST_SYMBOL: continue  # SKIP ALL FAKE $BASE
            if len(sym)>10: continue # Skip long scam names

            mcap = p.get('fdv',0) or 0
            liq = p.get('liquidity',{}).get('usd',0) or 0
            vol = p.get('volume',{}).get('h24',0) or 0

            # Anti-scam filters
            if not (2000 < mcap < 80000): continue
            if liq < 4000: continue
            if vol < 100: continue # This removes those $0 VOL $BASE scams you posted

            return {'symbol':sym,'address':p['baseToken']['address'],'mcap':mcap,'liq':liq,'vol':vol,'pair':p['pairAddress']}
    except Exception as e: print(e)
    return None

def bot_loop():
    time.sleep(3)
    send_msg("🔥 V8 ANTI-SCAM ONLINE - Blacklisted fake $BASE tokens - Now hunting REAL gems")
    seen=set([b.lower() for b in BLACKLIST_ADDR])
    while True:
        try:
            time.sleep(60)
            gem=get_gem(seen)
            if gem:
                seen.add(gem['address'].lower())
                send_msg(f"""🚀 NEW REAL GEM: ${gem['symbol']}

CA:
`{gem['address']}`

💰 MCAP: ${int(gem['mcap']):,}
💧 LIQ: ${int(gem['liq']):,}
📊 VOL: ${int(gem['vol']):,}

📈 https://dexscreener.com/base/{gem['pair']}

— FLIP PLAN —
BUY if <30min old
SELL 2x=50% 3x=80%""")
        except Exception as e:
            print(e); time.sleep(10)

@app.route('/')
def home(): return "V8 Anti-Scam Running"
threading.Thread(target=bot_loop,daemon=True).start()
if __name__=='__main__': app.run(host='0.0.0.0',port=10000)
