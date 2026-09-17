import os, time, asyncio, requests, threading
from flask import Flask
from telegram.ext import Application

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0") or 0)

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive! MASTER AI ONLINE"
seen = {}

def is_gem(p):
    try:
        if not 6000 <= float(p.get('fdv',0)) <= 28000: return False,""
        if float(p.get('liquidity',{}).get('usd',0)) < 900: return False,""
        if p.get('txns',{}).get('h1',{}).get('buys',0) < 20: return False,""
        if float(p.get('priceChange',{}).get('h1',0)) < 15: return False,""
        if float(p.get('volume',{}).get('h1',0)) < 5000: return False,""
        return True, "SAFE LP BURNED"
    except: return False,""

async def trader(b):
    await b.bot.send_message(chat_id=CHANNEL_ID, text="🤖 MASTER AI ONLINE")
    while True:
        try:
            d = requests.get("https://api.dexscreener.com/latest/dex/search/?q=pump.fun", timeout=15).json()
            for pair in d.get('pairs',[])[:40]:
                addr = pair['baseToken']['address']
                if addr in seen: continue
                gem,_ = is_gem(pair)
                if not gem: continue
                seen[addr] = {'s':pair['baseToken']['symbol'], 'pk':float(pair['fdv']), 'h':0}
                await b.bot.send_message(chat_id=CHANNEL_ID, text=f"💎 CALL ${seen[addr]['s']}\nMCap: ${pair['fdv']}\n{addr}")
            for addr, inf in list(seen.items()):
                try:
                    r = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{addr}", timeout=10).json()
                    now = float(r['pairs'][0].get('fdv',0))
                    if now <= 0: continue
                    if now > inf['pk']:
                        x = now/inf['pk']; seen[addr]['pk']=now
                        if x>2 and inf['h']<2:
                            await b.bot.send_message(chat_id=CHANNEL_ID, text=f"🚀 2X ${inf['s']} HOLD"); seen[addr]['h']=2
                        if x>5 and inf['h']<5:
                            await b.bot.send_message(chat_id=CHANNEL_ID, text=f"🔥 5X ${inf['s']} HOLD"); seen[addr]['h']=5
                        if x>10 and inf['h']<10:
                            await b.bot.send_message(chat_id=CHANNEL_ID, text=f"💰 10X ${inf['s']} Take 20%"); seen[addr]['h']=10
                        if x>25 and inf['h']<25:
                            await b.bot.send_message(chat_id=CHANNEL_ID, text=f"💎 25X ${inf['s']} SELL 50%"); seen[addr]['h']=25
                        if x>50 and inf['h']<50:
                            await b.bot.send_message(chat_id=CHANNEL_ID, text=f"🌙 50X ${inf['s']} SELL 80%"); seen[addr]['h']=50
                except: continue
            await asyncio.sleep(10)
        except: await asyncio.sleep(10)

async def main():
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT',10000)))).start()
    bot_app = Application.builder().token(BOT_TOKEN).build()
    await trader(bot_app)

if __name__ == "__main__": asyncio.run(main())
