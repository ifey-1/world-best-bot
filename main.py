import asyncio
from dotenv import load_dotenv
from scanner import scan_tokens
from poster import post_call
load_dotenv()
print("=== IFEYSYCO WORLD BEST BOT STARTED ===")
async def run():
    seen = set()
    while True:
        try:
            gems = scan_tokens()
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
if __name__ == "__main__":
    asyncio.run(run())
