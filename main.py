import os
import time
import requests
import asyncio
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@ifeysycoai")
# For testing without Telegram, it will just print in logs

# ===== V8 ANTI-SCAM FILTER =====
def is_valid_gem(pair):
    try:
        mcap = pair.get('fdv', 0) or 0
        liquidity = pair.get('liquidity', {}).get('usd', 0) or 0
        vol_5m = pair.get('volume', {}).get('m5', 0) or 0
        
        # Your V9 rules: $8K-$25K
        if not (8000 <= mcap <= 25000):
            return False
        if liquidity < 3000:
            return False
        if vol_5m < 500:  # needs real buys
            return False
        # Block obvious scams
        if pair.get('baseToken', {}).get('name','').lower() in ['scam','honeypot','test']:
            return False
        return True
    except:
        return False

def scan_tokens():
    gems = []
    # Scan Base + Solana new pairs
    for chain in ['solana', 'base']:
        try:
            url = f"https://api.dexscreener.com/latest/dex/search/?q={chain}"
            r = requests.get(url, timeout=10)
            data = r.json()
            for pair in data.get('pairs', [])[:30]:
                if pair.get('chainId') != chain:
                    continue
                if is_valid_gem(pair):
                    gems.append({
                        'chain': chain,
                        'name': pair['baseToken']['symbol'],
                        'address': pair['baseToken']['address'],
                        'mcap': int(pair.get('fdv',0)),
                        'liq': int(pair.get('liquidity',{}).get('usd',0)),
                        'price': pair.get('priceUsd','0'),
                        'url': pair.get('url','')
                    })
        except Exception as e:
            print(f"Scan error {chain}: {e}")
    return gems

async def post_to_telegram(gem):
    if not BOT_TOKEN:
        print(f"FOUND GEM (No BOT_TOKEN set): {gem}")
        return
    
    bot = Bot(token=BOT_TOKEN)
    text = f"""🔥 IFEYSYCO AI V9 GEM 🔥

Token: ${gem['name']}
Chain: {gem['chain'].upper()}
Entry MC: ${gem['mcap']:,}
Liquidity: ${gem['liq']:,}

Contract: `{gem['address']}`

Chart: {gem['url']}

Strategy: $2.5 in | Sell 2x / 5x / 10x
Bot: @ifeysycoai
"""
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode='Markdown')
        print(f"Posted {gem['name']}")
    except Exception as e:
        print(f"Telegram error: {e}")
        print(text)

async def main():
    print("=== IFEYSYCO WORLD BEST BOT STARTED ===")
    print("Scanning Base + Solana $8K-$25K V9 Filter")
    seen = set()
    
    while True:
        try:
            gems = scan_tokens()
            if not gems:
                print("No gems this scan - market quiet, holding...")
            for gem in gems:
                if gem['address'] in seen:
                    continue
                seen.add(gem['address'])
                await post_to_telegram(gem)
                await asyncio.sleep(5)
            await asyncio.sleep(15)
        except Exception as e:
            print(f"Loop error: {e}")
            await asyncio.sleep(15)

if __name__ == "__main__":
    asyncio.run(main())
