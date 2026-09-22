import os
from telegram import Bot
from image_gen import create_call_image

async def post_call(token):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return

    try:
        bot = Bot(token=bot_token)
        img_path = create_call_image(token)
        
        caption = f"""🔥 IFEYSYCO GEM ALERT 🔥

💎 ${token['name']} | {token['chain'].upper()}
💰 MC: ${token['mcap']:,}
💧 Liq: ${token['liq']:,}

📝 Contract:
`{token['address']}`

📊 Chart: {token['url']}

🚀 @ifeysycoai"""

        with open(img_path, 'rb') as photo:
            await bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, parse_mode='Markdown')
        print(f"Posted {token['name']} success")
    except Exception as e:
        print(f"Post failed: {e}")
