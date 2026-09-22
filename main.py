import os
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
import asyncio
import threading

load_dotenv()
app = FastAPI()

@app.get("/")
def home():
    return {"status": "IFEYSYCO BOT IS LIVE", "message": "Bot is running on free tier"}

@app.get("/health")
def health():
    return {"ok": True}

def start_bot_loop():
    import time
    from scanner import scan_tokens
    from poster import post_call
    import asyncio as aio
    async def run_loop():
        print("=== BOT LOOP STARTED ===")
        seen = set()
        while True:
            try:
                print("Scanning for gems...")
                gems = scan_tokens()
                print(f"Found {len(gems)} potential gems")
                for g in gems:
                    if g['address'] not in seen:
                        seen.add(g['address'])
                        await post_call(g)
                        print(f"Posted {g['name']}")
                await aio.sleep(20)
            except Exception as e:
                print(f"Loop error: {e}")
                await aio.sleep(20)
    aio.run(run_loop())

@app.on_event("startup")
def on_startup():
    thread = threading.Thread(target=start_bot_loop, daemon=True)
    thread.start()
    print("Background bot thread started")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
