import os, asyncio
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
from scanner import scan_tokens
from poster import post_call

load_dotenv()

app = FastAPI()

@app.get("/")
def home():
    return {"status": "IFEYSYCO WORLD BEST BOT IS LIVE", "expert_mode": os.getenv("EXPERT_MODE")}

@app.get("/health")
def health():
    return {"ok": True}

async def bot_loop():
    print("=== IFEYSYCO WORLD BEST BOT STARTED (FREE MODE) ===")
    print(f"BOT TOKEN EXISTS: {bool(os.getenv('TELEGRAM_BOT_TOKEN'))}")
    print(f"CHAT ID: {os.getenv('TELEGRAM_CHAT_ID')}")
    seen = set()
    while True:
        try:
            gems = scan_tokens()
            if not gems:
                print("No gems - scanning again...")
            for g in gems:
                if g['address'] in seen:
                    continue
                seen.add(g['address'])
                print(f"POSTING: {g['name']} at ${g['mcap']}")
                await post_call(g)
                await asyncio.sleep(5)
            await asyncio.sleep(15)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(15)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(bot_loop())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
