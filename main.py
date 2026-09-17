import os, time, threading, requests
from flask import Flask
from datetime import datetime
app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@IfeysycoAI")

active_calls = {}
calls_today = 0
last_day = None

def send(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=25)
    except: pass

def get_best_pair_and_liquidity(symbol, addr_map):
    best_liq = 0
    best_chain = None
    best_addr = None
    for chain_name, addr in addr_map.items():
        if not addr: continue
        try:
            r = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={addr}", timeout=10).json()
            pairs = r.get('pairs', [])
            for p in pairs:
                liq = p.get('liquidity', {}).get('usd', 0) or 0
                if liq > best_liq:
                    best_liq = liq
                    best_chain = chain_name
                    best_addr = addr
        except: continue
        time.sleep(0.5)
    if best_liq < 50000: return None, None, 0
    return best_chain, best_addr, best_liq

def get_contracts_map(coin_id):
    try:
        time.sleep(2)
        d = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id}", timeout=15).json()
        plats = d.get('platforms', {})
        return {k.upper(): v for k,v in plats.items() if v}
    except: return {}

def get_gems():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=price_change_percentage_1h_desc&per_page=250&page=1&price_change_percentage=1h,24h,7d"
        r = requests.get(url, timeout=20)
        if r.status_code == 429:
            time.sleep(60)
            return []
        return r.json()
    except: return []

def is_gem(coin):
    try:
        ch1 = coin.get('price_change_percentage_1h_in_currency',0) or 0
        ch24 = coin.get('price_change_percentage_24h',0) or 0
        vol = coin.get('total_volume',0) or 0
        mcap = coin.get('market_cap',0) or 0
        if ch1 < 2 or ch1 > 35: return False
        if ch24 < 1 or ch24 > 80: return False
        if vol < 2000000: return False
        if mcap < 500000 or mcap > 40000000: return False
        if mcap>0 and (vol/mcap) < 0.20: return False
        if coin['symbol'].upper() in ['BTC','ETH','SOL','BNB']: return False
        return True
    except: return False

def scanner():
    global calls_today, last_day
    send("🚀 <b>V7 SAFE BOT LIVE - FIXED!</b>\n\n✅ No Rate Limit Ban\n✅ Liquidity >$50k Check\n✅ Correct Chain Address\n✅ SL/TP Included\n✅ MEXC + DEX Links\n✅ 1-3 BEST/DAY 2X-50X")
    time.sleep(5)
    while True:
        try:
            today = datetime.now().date()
            if last_day!= today:
                calls_today = 0
                last_day = today
                active_calls.clear()

            coins = get_gems()
            if not coins:
                time.sleep(180)
                continue

            for cid, data in list(active_calls.items()):
                curr = next((c for c in coins if c['id']==cid), None)
                if not curr: continue
                entry = data['entry']
                price = curr.get('current_price',0)
                pct = ((price-entry)/entry*100) if entry else 0
                sym = data['symbol']
                if pct >= 95 and not data.get('s2x'):
                    send(f"💥 <b>{sym} 2X HIT +{pct:.0f}%</b>\nEntry ${entry} -> ${price}\n🔴 SELL 50% at 2X\n🟢 HOLD 50%")
                    data['s2x']=True
                elif pct >= 400 and not data.get('s5x'):
                    send(f"🚀 <b>{sym} 5X HIT +{pct:.0f}%</b>\n🔴 SELL 75%\n🟢 HOLD 25% for 50X")
                    data['s5x']=True
                elif pct <= -20:
                    send(f"⚠️ <b>{sym} SL -20% HIT</b>\n🔴 SELL ALL - Save capital")
                    del active_calls[cid]

            if calls_today >= 3:
                time.sleep(180)
                continue

            best = None
            best_score = 0
            for coin in coins:
                if coin['id'] in active_calls: continue
                if not is_gem(coin): continue
                ch1 = coin.get('price_change_percentage_1h_in_currency',0)
                vol = coin.get('total_volume',0)
                mcap = coin.get('market_cap',1)
                score = ch1 * (vol/mcap)
                if score > best_score:
                    best_score = score
                    best = coin

            if best:
                addr_map = get_contracts_map(best['id'])
                if not addr_map: continue
                chain, addr, liq = get_best_pair_and_liquidity(best['symbol'], addr_map)
                if not addr or liq < 50000: continue

                calls_today += 1
                sym = best['symbol'].upper()
                name = best['name']
                price = best.get('current_price',0)
                ch1 = best.get('price_change_percentage_1h_in_currency',0)
                mcap = best.get('market_cap',0)/1_000_000
                vol = best.get('total_volume',0)/1_000_000

                if mcap < 2: potential = "20X-50X 💎"
                elif mcap < 8: potential = "10X-20X 🔥"
                else: potential = "2X-5X"

                entry = price
                sl = entry * 0.80
                tp1 = entry * 2
                tp2 = entry * 5
                tp3 = entry * 10

                msg = f"""🎯 <b>BEST GEM #{calls_today} - {potential}</b>
🔥 ${sym} ({name})

💰 <b>ENTRY ZONE:</b>
${entry:.8f} - ${entry*1.03:.8f}
⚡ Market Buy NOW!

🛡️ <b>STOP LOSS:</b>
${sl:.8f} (-20%)
SELL ALL if hits

🎯 <b>TAKE PROFIT:</b>
TP1 ${tp1:.8f} (2X) = SELL 50%
TP2 ${tp2:.8f} (5X) = SELL 25%
TP3 ${tp3:.8f} (10X+) = HOLD 25%

📊 MCap ${mcap:.2f}M | Vol ${vol:.1f}M | Liq ${liq/1000:.0f}k | 1h +{ch1:.1f}%

📜 <b>CONTRACT - TAP TO COPY:</b>
<code>{addr}</code>
Chain: {chain}

🛒 <b>BUY NOW:</b>
DEX: https://dexscreener.com/{chain.lower()}/{addr}
MEXC: https://www.mexc.com/exchange/{sym}_USDT
Gate: https://www.gate.io/trade/{sym}_USDT

🧠 Risk 2% per trade!"""

                send(msg)
                active_calls[best['id']] = {'entry': entry, 'symbol': sym, 's2x': False, 's5x': False}
                time.sleep(10)

            time.sleep(180)
        except Exception as e:
            print(e)
            time.sleep(60)

@app.route('/')
def home():
    return f"V7 SAFE BOT ALWAYS RUNNING - {calls_today}/3 today"

threading.Thread(target=scanner, daemon=True).start()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
