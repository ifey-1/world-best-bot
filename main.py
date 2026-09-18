import os, time, requests, threading
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHAT_ID")
BLACKLIST = ["0xb2000000000000000000000005b21d8272a739ea01"]

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": CHANNEL_ID,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }, timeout=15)
    except Exception as e:
        print(f"Telegram err {e}")

def get_gem(seen):
    try:
        urls = [
            "https://api.dexscreener.com/latest/dex/pairs/base",
            "https://api.dexscreener.com/latest/dex/search/?q=base"
        ]
        for api_url in urls:
            data = requests.get(api_url, timeout=15).json()
            pairs = data.get('pairs', [])[:120]
            for p in pairs:
                if p.get('chainId') != 'base':
                    continue
                base = p.get('baseToken', {})
                addr = base.get('address','').lower()
                if not addr or addr in seen:
                    continue
                if addr in [b.lower() for b in BLACKLIST]:
                    continue

                mcap = p.get('fdv',0) or 0
                liq = p.get('liquidity',{}).get('usd',0) or 0
                vol = p.get('volume',{}).get('h24',0) or 0
                symbol = base.get('symbol','UNK')

                # V6 FILTERS - LOOSE TO GUARANTEE CALLS
                if not (800 < mcap < 120000):
                    continue
                if liq < 2500:  # Will call
                    continue
                if vol < 50:    # Will call
                    continue

                return {
                    'symbol': symbol.upper(),
                    'address': p['baseToken']['address'],
                    'mcap': mcap,
                    'liq': liq,
                    'vol': vol,
                    'pair': p.get('pairAddress','')
                }
    except Exception as e:
        print(f"Scan err {e}")
    return None

def bot_loop():
    time.sleep(5)
    send_msg("🔥 V6 FINAL ONLINE - READY FOR $10->$100\n\nFilters: MCAP 800-120k LIQ>2.5k\nFirst call in 30 seconds!")
    seen = set([b.lower() for b in BLACKLIST])
    first = True
    while True:
        try:
            sleep_time = 30 if first else 90
            time.sleep(sleep_time)
            first = False
            
            gem = get_gem(seen)
            
            if gem:
                seen.add(gem['address'].lower())
                msg = f"""🚀 NEW GEM: ${gem['symbol']}

CA:
`{gem['address']}`

💰 MCAP: ${int(gem['mcap']):,}
💧 LIQ: ${int(gem['liq']):,}
📊 VOL: ${int(gem['vol']):,}

📈 CHART: https://dexscreener.com/base/{gem['pair']}

— — FLIP PLAN — —
✅ BUY: Only if chart <1hr old & flat start
❌ SKIP: If already up 5x

💸 SELL PLAN:
• At 2x -> SELL 50% (secure capital)
• At 3x -> SELL 80% (take profit)
• Leave 20% moonbag

This is how $10 -> $100"""

                send_msg(msg)
                print(f"Posted {gem['symbol']}")
            else:
                send_msg("✅ Bot alive - scanning Base... no safe gem this round, next scan in 90s")
                print("No gem this round")

        except Exception as e:
            print(f"Loop err {e}")
            time.sleep(15)

@app.route('/')
def home():
    return "V6 FINAL Running - $10 to $100 mode"

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
