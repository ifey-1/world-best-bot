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
BLACKLIST_SYMBOL = ["BASE","WETH","USDC","USDT","WBASE","SOL","WSOL","USDC"]

def send_msg(t):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id":CHANNEL_ID,"text":t,"parse_mode":"Markdown","disable_web_page_preview":True},timeout=10)
    except: pass

def get_gem(seen, chain):
    try:
        # Search chain
        r = requests.get(f"https://api.dexscreener.com/latest/dex/search/?q={chain}",timeout=15).json()
        pairs = sorted(r.get('pairs',[]), key=lambda x: x.get('pairCreatedAt',0) or 0, reverse=True)[:150]
        for p in pairs:
            if p.get('chainId')!=chain: continue
            sym = p.get('baseToken',{}).get('symbol','').upper()
            addr = p.get('baseToken',{}).get('address','').lower()
            if not addr or addr in seen: continue
            if addr in [b.lower() for b in BLACKLIST_ADDR]: continue
            if sym in BLACKLIST_SYMBOL: continue
            if len(sym)>12: continue

            mcap = p.get('fdv',0) or p.get('marketCap',0) or 0
            liq = p.get('liquidity',{}).get('usd',0) or 0
            h1 = p.get('priceChange',{}).get('h1',0) or 0
            m5_buys = p.get('txns',{}).get('m5',{}).get('buys',0) or 0

            # === V9 EARLY-HOLD FILTERS - LET IT MOVE ===
            if not (8000 < mcap < 25000): continue  # Super early like $14.3K
            if liq < 1500: continue
            if h1 > 70: continue  # Skip already pumped tops
            if m5_buys < 1: continue
            if len(seen) > 5000: seen.clear() # reset

            return {'symbol':sym,'address':p['baseToken']['address'],'mcap':mcap,'liq':liq,'h1':h1,'buys':m5_buys,'pair':p['pairAddress'],'chain':chain}
    except Exception as e: print(f"{chain} error", e)
    return None

def bot_loop():
    time.sleep(3)
    send_msg("🔥 *V9-DUAL EARLY-HOLD ONLINE*\nBase + Solana hunting $8K-$25K\n1 call per 1-2 days - but 10x-50x setup. Let it move!")
    seen=set([b.lower() for b in BLACKLIST_ADDR])
    while True:
        try:
            for chain in ["solana", "base"]: # SOL first - more 100x
                gem=get_gem(seen, chain)
                if gem:
                    seen.add(gem['address'].lower())
                    send_msg(f"""🔥 *V9 EARLY GEM - LET IT MOVE* [{gem['chain'].upper()}]

💎 ${gem['symbol']} | MC ${int(gem['mcap']):,}
💧 LIQ ${int(gem['liq']):,} | 1H {gem['h1']}% | Buys {gem['buys']}

CA:
`{gem['address']}`

📈 https://dexscreener.com/{gem['chain']}/{gem['pair']}

— *PLAN - LET IT MOVE 2 DAYS* —
BUY $2 NOW at ${int(gem['mcap']):,}
SELL 2x = 50% (free bag)
SELL 5x = 25%
HOLD 25% for 48H for 10x-50x

Don't scalp. Let it move.""")
                    time.sleep(5) # avoid spam
            time.sleep(45)
        except Exception as e:
            print(e); time.sleep(10)

@app.route('/')
def home(): return "V9-DUAL EARLY-HOLD Running - $8K-$25K"
threading.Thread(target=bot_loop,daemon=True).start()
if __name__=='__main__': app.run(host='0.0.0.0',port=10000)
