import os, time, threading, requests
from flask import Flask
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@IfeysycoAI")

active_calls = {}
calls_today = 0
last_day = None

CHAIN_MAP = {
    "ethereum": ("ethereum", "1"),
    "binance-smart-chain": ("bsc", "56"),
    "bsc": ("bsc", "56"),
    "base": ("base", "8453"),
    "arbitrum-one": ("arbitrum", "42161"),
    "polygon-pos": ("polygon", "137"),
    "avalanche": ("avalanche", "43114"),
    "solana": ("solana", None)
}

def send(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=25)
    except Exception as e:
        print(f"Send error {e}")

# ===== EXPERT SAFETY =====
def check_goplus(chain_id_num, addr):
    """Returns (is_safe, reason)"""
    if not chain_id_num: # Solana - skip GoPlus
        return True, "Solana skipped"
    try:
        url = f"https://api.gopluslabs.io/api/v1/token_security/{chain_id_num}?contract_addresses={addr}"
        r = requests.get(url, timeout=12).json()
        data = r.get('result', {}).get(addr.lower(), {}) or r.get('result', {}).get(addr, {})
        if not data:
            return False, "No GoPlus data"

        # Critical checks
        if data.get('is_honeypot') == '1':
            return False, "HONEYPOT"
        buy_tax = float(data.get('buy_tax', 0) or 0)
        sell_tax = float(data.get('sell_tax', 0) or 0)
        if buy_tax > 10 or sell_tax > 10:
            return False, f"High Tax {buy_tax}/{sell_tax}%"
        if data.get('is_proxy') == '1' and data.get('is_mintable') == '1':
            return False, "Mintable Proxy"
        if data.get('is_blacklisted') == '1':
            return False, "Blacklisted"
        if data.get('can_take_back_ownership') == '1':
            return False, "Can take back ownership"
        if data.get('owner_percent', 0):
            try:
                if float(data.get('owner_percent',0)) > 15:
                    return False, f"Owner {data.get('owner_percent')}%"
            except: pass
        if data.get('creator_percent', 0):
            try:
                if float(data.get('creator_percent',0)) > 15:
                    return False, f"Creator {data.get('creator_percent')}%"
            except: pass
        # Holder concentration
        try:
            hp = float(data.get('holder_count', 9999) or 0)
            if hp < 50:
                return False, f"Only {hp} holders"
        except: pass

        return True, "Safe"
    except Exception as e:
        print(f"GoPlus error {e}")
        return True, f"GoPlus err skip: {e}" # Don't block if API down

def get_best_pair_and_liquidity(addr_map):
    best = None
    best_liq = 0

    for cg_chain, token_addr in addr_map.items():
        if not token_addr: continue
        map_data = CHAIN_MAP.get(cg_chain.lower())
        if not map_data: continue
        dex_chain, goplus_id = map_data

        try:
            r = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{token_addr}", timeout=10).json()
            pairs = r.get('pairs', []) or []
            pairs = sorted(pairs, key=lambda x: x.get('liquidity',{}).get('usd',0) or 0, reverse=True)

            for p in pairs[:3]: # Check top 3 pairs
                liq = p.get('liquidity', {}).get('usd', 0) or 0
                if liq < 30000: continue
                if liq <= best_liq: continue

                fdv = p.get('fdv', 0) or 0
                mcap = p.get('marketCap', fdv) or fdv
                # Expert filters on pair
                if mcap and mcap < 50000: continue # Too small = scam

                pair_created = p.get('pairCreatedAt')
                if pair_created:
                    age_hours = (time.time()*1000 - pair_created)/1000/3600
                    if age_hours < 2: # Less than 2h = too risky for auto bot
                        continue

                # Volume check
                vol24 = p.get('volume', {}).get('h24', 0) or 0
                if vol24 < 20000: continue

                # SECURITY CHECK
                pair_token_addr = p.get('baseToken', {}).get('address') or token_addr
                is_safe, reason = check_goplus(goplus_id, pair_token_addr)
                if not is_safe:
                    print(f"Blocked {pair_token_addr} {dex_chain} - {reason}")
                    continue

                # Passed all
                best_liq = liq
                best = p
                best['goplus_reason'] = reason
                best['checked_addr'] = pair_token_addr

        except Exception as e:
            print(f"Dex error {e}")
            continue
        time.sleep(0.6)

    if not best:
        return None, None, 0, None, "No safe pair"
    return best.get('chainId'), best.get('pairAddress'), best_liq, best.get('url'), best.get('goplus_reason')

def get_contracts_map(coin_id):
    try:
        time.sleep(1.5)
        d = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id}", timeout=15).json()
        plats = d.get('platforms', {})
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
        if ch1 < 2.5 or ch1 > 40: return False
        if ch24 < 2 or ch24 > 90: return False
        if vol < 2000000: return False
        if mcap < 500000 or mcap > 40000000: return False
        if mcap>0 and (vol/mcap) < 0.20: return False
        if coin['symbol'].upper() in ['BTC','ETH','SOL','BNB','XRP','DOGE']: return False
        return True
    except: return False

def scanner():
    global calls_today, last_day
    send("🚀 <b>V8 EXPERT ANTI-RUG LIVE!</b>\n✅ GoPlus | Tax Check | Honeypot | Owner Check | Holder Check")
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

            # Track SL/TP
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
                chain, pair_addr, liq, pair_url, safety = get_best_pair_and_liquidity(addr_map)
                if not pair_addr:
                    print(f"Skipped {best['symbol']} - {safety}")
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
✅ Safety: {safety}

📜 PAIR:
<code>{pair_addr}</code>
Chain: {chain}

🛒 BUY:
DEX: {dex_link}
MEXC: https://www.mexc.com/exchange/{sym}_USDT

🧠 Risk 2% per trade! Expert Filtered!"""

                send(msg)
                active_calls[best['id']] = {'entry': entry, 'symbol': sym, 's2x': False, 's5x': False}
                time.sleep(10)

            time.sleep(180)
        except Exception as e:
            print(f"Scanner error: {e}")
            time.sleep(60)

@app.route('/')
def home():
    return f"V8 EXPERT RUNNING - {calls_today}/3 today - {len(active_calls)} active"

threading.Thread(target=scanner, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
