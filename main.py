import os, time, requests, threading
from flask import Flask

app = Flask(__name__)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHAT_ID")

# Blacklist of bad coins you saw
BLACKLIST = [
    "0xb2000000000000000000000005b21d8272a739ea01".lower(),
]

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHANNEL_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}, timeout=10)
    except Exception as e:
        print(f"Send error: {e}")

def get_safe_gem(seen):
    try:
        # Search Base - newest boosted
        r = requests.get("https://api.dexscreener.com/latest/dex/search/?q=base", timeout=15).json()
        pairs = r.get('pairs', [])[:50]
        
        for p in pairs:
            try:
                if p.get('chainId') != 'base': continue
                addr = p.get('baseToken', {}).get('address', '').lower()
                if addr in BLACKLIST or addr in seen: continue
                
                mcap = p.get('fdv', 0) or 0
                liq = p.get('liquidity', {}).get('usd', 0) or 0
                vol = p.get('volume', {}).get('h24', 0) or 0
                symbol = p.get('baseToken', {}).get('symbol', 'UNKNOWN')
                name = p.get('baseToken', {}).get('name', '').lower()
                
                # V4 SAFETY FILTERS
                if not (8000 < mcap < 70000): continue
                if liq < 12000: continue  # Fix low liquidity warning
                if vol < 1000: continue   # Must have real volume
                if len(symbol) > 12: continue
                if len(symbol) < 2: continue
                # Ban spam words
                if any(x in name for x in ['brian', 'gay', 'basedbald', 'porn', 'sex']): continue
                
                return {
                    'symbol': symbol.upper(),
                    'address': p['baseToken']['address'],
                    'mcap': mcap,
                    'liq': liq,
                    'vol': vol,
                    'pair': p['pairAddress']
                }
            except: continue
    except Exception as e:
        print(f"Scan error: {e}")
    return None

def bot_loop():
    time.sleep(10)
    send_msg("🛡️ V4 SAFE SCANNER ONLINE ✅\n\nFilters: LIQ>$12k VOL>$1k MCAP $8k-70k\nNo more spam. Blacklisted bad $BASE\n\nScanning...")
    
    seen = set([a.lower() for a in BLACKLIST])
    while True:
        try:
            time.sleep(180) # 3 mins
            gem = get_safe_gem(seen)
            if gem:
                seen.add(gem['address'].lower())
                msg = f"""🚀 SAFE GEM FOUND: ${gem['symbol']}

CA:
`{gem['address']}`

💰 MCAP: ${int(gem['mcap']):,}
💧 LIQ: ${int(gem['liq']):,} ✅ Safe
📊 VOL 24h: ${int(gem['vol']):,}
⛓️ Chain: BASE

📈 https://dexscreener.com/base/{gem['pair']}

⚠️ DYOR - Early gem but safe filters passed!"""
                send_msg(msg)
                print(f"Posted {gem['symbol']}")
            else:
                print("No safe gem this round")
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(30)

@app.route('/')
def home():
    return "V4 Bot Running - No Spam"

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
