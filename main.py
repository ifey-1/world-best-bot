import os, time, threading, requests
from flask import Flask
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@IfeysycoAI")

active_calls = {}
calls_today = 0
last_day = None

# FIX 1: Chain map
CHAIN_MAP = {
    "ethereum": "ethereum",
    "binance-smart-chain": "bsc",
    "bsc": "bsc",
    "solana": "solana",
    "base": "base",
    "arbitrum-one": "arbitrum",
    "polygon-pos": "polygon",
    "avalanche": "avalanche"
}

def send(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=25)
    except: pass

def get_best_pair_and_liquidity(addr_map):
    best_liq = 0
    best_chain = None
    best_addr = None
    best_pair_url = None

    for cg_chain, addr in addr_map.items():
        if not addr: continue
        dex_chain = CHAIN_MAP.get(cg_chain.lower())
        if not dex_chain: continue
        try:
            # FIX 2: Use tokens endpoint not search
            r = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{addr}", timeout=10).json()
            pairs = r.get('pairs', []) or []
            # Sort by liquidity
            pairs = sorted(pairs, key=lambda x: x.get('liquidity',{}).get('usd',0) or 0, reverse=True)
            for p in pairs:
                liq = p.get('liquidity', {}).get('usd', 0) or 0
                if liq > best_liq:
                    best_liq = liq
                    best_chain = p.get('chainId', dex_chain)
                    best_addr = p.get('pairAddress', addr)
                    best_pair_url = p.get('url')
        except: continue
        time.sleep(0.6)

    if best_liq < 30000: # Lowered for early memes
        return None, None, 0, None
    return best_chain, best_addr, best_liq, best_pair_url

def get_contracts_map(coin_id):
    try:
        time.sleep(1.5)
        d = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id}", timeout=15).json()
        plats = d.get('platforms', {})
        # Keep original keys for mapping
        return {k: v for k,v in plats.items() if v}
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
        if ch1 < 2 or ch1 > 45: return False
        if ch24 < 1 or ch24 > 120: return False
        if vol < 1500000: return False
        if mcap < 300000 or mcap > 50000000: return False
        if mcap>0 and (vol/mcap) < 0.15: return False
        if coin['symbol'].upper() in ['BTC','ETH','SOL','BNB','XRP']: return False
        return True
    except: return False

def scanner():
    global calls_today, last_day
    send("🚀 <b>V7.1 FIXED LIVE!</b>\n✅ Chain Map Fixed | Token API | Solana Ready")
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
                if not price or not entry: continue
                pct = ((price-entry)/entry*100)
                sym = data['symbol']
                if pct >= 95 and not data.get('s2x'):
                    send(f"💥 <b>{sym} 2X HIT +{pct:.0f}%</b>\nEntry ${entry} -> ${price}\n🔴 SELL 50% at 2X | HOLD 50%")
                    data['s2x']=True
                elif pct >= 400 and not data.get('s5x'):
                    send(f"🚀 <b>{sym} 5X HIT +{pct:.0f}%</b>\n🔴 SELL 75% | HOLD 25% for 50X")
                    data['s5x']=True
                elif pct <= -20:
                    send(f"⚠️ <b>{sym} SL -20% HIT</b>\n🔴 SELL ALL")
                    del active_calls[cid]

            if calls_today >= 3:
                time.sleep(180)
                continue

            best = None
            best_score = 0
            for coin in coins:
                if coin['id'] in active_calls: continue
                if not is_gem(coin): continue
                ch1 = coin.get('price_change_percentage_1h_in_currency',0) or 0
                vol = coin.get('total_volume',0)
                mcap = coin.get('market_cap',1)
                score = ch1 * (vol/mcap) if mcap else 0
                if score > best_score:
                    best_score = score
                    best = coin

            if best:
                addr_map = get_contracts_map(best['id'])
                if not addr_map:
                    time.sleep(2)
                    continue
                chain, pair_addr, liq, pair_url = get_best_pair_and_liquidity(addr_map)
                if not pair_addr or liq < 30000:
                    time.sleep(2)
                    continue

                calls_today += 1
                sym = best['symbol'].upper()
                name = best['name']
                price = best.get('current_price',0)
                ch1 = best.get('price_change_percentage_1h_in_currency',0)
                mcap = best.get('market_cap',0)/1_000_000
                vol = best.get('total_volume',0)/1_000_000

                if mcap < 2: potential = "20X-50X MEME 💎"
                elif mcap < 8: potential = "10X-20X 🔥"
                else: potential = "2X-5X"

                entry = price
                sl = entry * 0.80
                tp1 = entry * 2
                tp2 = entry * 5

                dex_link = pair_url or f"https://dexscreener.com/{chain}/{pair_addr}"

                msg = f"""🎯 <b>BEST GEM #{calls_today} - {potential}</b>
🔥 ${sym} ({name})

💰 ENTRY: ${entry:.8f} - ${entry*1.03:.8f}
⚡ Market Buy NOW!

🛡️ SL: ${sl:.8f} (-20%)
🎯 TP1 ${tp1:.8f} (2X) = SELL 50%
🎯 TP2 ${tp2:.8f} (5X) = SELL 25%

📊 MCap ${mcap:.2f}M | Vol ${vol:.1f}M | Liq ${liq/1000:.0f}k | 1h +{ch1:.1f}%

📜 PAIR:
<code>{pair_addr}</code>
Chain: {chain}

🛒 BUY:
DEX: {dex_link}
MEXC: https://www.mexc.com/exchange/{sym}_USDT

🧠 Risk 2% per trade!"""

                send(msg)
                active_calls[best['id']] = {'entry': entry, 'symbol': sym, 's2x': False, 's5x': False}
                time.sleep(10)

            time.sleep(180)
        except Exception as e:
            print(f"Scanner error: {e}")
            time.sleep(60)

@app.route('/')
def home():
    return f"V7.1 FIXED RUNNING - {calls_today}/3 today - {len(active_calls)} active"

threading.Thread(target=scanner, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
