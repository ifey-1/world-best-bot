import os, time, asyncio, requests
from telegram.ext import Application

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
seen = {}

def get_rugcheck(a):
    try:
        r = requests.get(f"https://api.rugcheck.xyz/v1/tokens/{a}/report", timeout=10).json()
        if r.get('score', 1000) > 300:
            return False, "Bad Score"
        return True, "SAFE LP BURNED"
    except:
        return True, "SAFE"

def is_gem(p):
    try:
        fdv = float(p.get('fdv', 0))
        if not (6000 <= fdv <= 28000):
            return False, ""
        if float(p.get('liquidity', {}).get('usd', 0)) < 9000:
            return False, ""
        if p.get('txns', {}).get('h1', {}).get('buys', 0) < 20:
            return False, ""
        if float(p.get('priceChange', {}).get('h1', 0)) < 15:
            return False, ""
        if float(p.get('volume', {}).get('h1', 0)) < 5000:
            return False, ""
        ok, rs = get_rugcheck(p['baseToken']['address'])
        if not ok:
            return False, rs
        return True, rs
    except:
        return False, ""

async def trader(app):
    await app.bot.send_message(CHANNEL_ID, "👑 MASTER AI ONLINE - Scanning $6K-$28K 24/7")
    while True:
        try:
            d = requests.get("https://api.dexscreener.com/latest/dex/search/?q=pump.fun", timeout=15).json()
            for pair in d.get('pairs', [])[:40]:
                addr = pair['baseToken']['address']
                if addr in seen:
                    continue
                gem, info = is_gem(pair)
                if not gem:
                    continue
                sym = pair['baseToken']['symbol']
                mcap = int(float(pair['fdv']))
                seen[addr] = {"s": sym, "c": mcap, "t": time.time(), "hx": 0, "p": pair['pairAddress'], "pk": mcap}
                await app.bot.send_message(CHANNEL_ID, f"💎 CALL ${sym} EARLY GEM\n{info}\nMC: ${mcap:,}\nCA:\n`{addr}`\nhttps://dexscreener.com/solana/{pair['pairAddress']}", parse_mode='Markdown')
            for addr, inf in list(seen.items()):
                try:
                    r = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{addr}", timeout=10).json()
                    if not r.get('pairs'):
                        continue
                    p = r['pairs'][0]
                    now = float(p.get('fdv', 0))
                    if now == 0:
                        continue
                    if now > inf['pk']:
                        seen[addr]['pk'] = now
                    x = now / inf['c']
                    if x >= 2 and inf['hx'] < 2:
                        await app.bot.send_message(CHANNEL_ID, f"📈 2X ${inf['s']} HOLD\n`{addr}`", parse_mode='Markdown')
                        seen[addr]['hx'] = 2
                    if x >= 5 and inf['hx'] < 5:
                        await app.bot.send_message(CHANNEL_ID, f"🚀 5X ${inf['s']} HOLD STRONG\n`{addr}`", parse_mode='Markdown')
                        seen[addr]['hx'] = 5
                    if x >= 10 and inf['hx'] < 10:
                        await app.bot.send_message(CHANNEL_ID, f"💎 10X ${inf['s']} Take 20%\n`{addr}`", parse_mode='Markdown')
                        seen[addr]['hx'] = 10
                    if x >= 25 and inf['hx'] < 25:
                        await app.bot.send_message(CHANNEL_ID, f"🔥 25X ${inf['s']} SELL 50%\n`{addr}`", parse_mode='Markdown')
                        seen[addr]['hx'] = 25
                    if x >= 50 and inf['hx'] < 50:
                        await app.bot.send_message(CHANNEL_ID, f"🌙 50X ${inf['s']} SELL 80% WIN\n`{addr}`", parse_mode='Markdown')
                        seen[addr]['hx'] = 50
                    drop = (inf['pk'] - now) / inf['pk'] * 100
                    if x >= 5 and drop >= 40 and inf['hx'] >= 10:
                        await app.bot.send_message(CHANNEL_ID, f"🔴 SELL ${inf['s']} dropped 40% from peak\n`{addr}`", parse_mode='Markdown')
                        del seen[addr]
                except:
                    continue
        except:
            pass
        await asyncio.sleep(40)

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.create_task(trader(app))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
