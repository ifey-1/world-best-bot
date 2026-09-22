import os
import telegram
from image_gen import create_call_image

async def post_call(token):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    channel = os.getenv("TELEGRAM_CHAT_ID", "@ifeysycoai")
    
    if not bot_token:
        print(f"GEM FOUND but no TELEGRAM_BOT_TOKEN set: {token}")
        return

    bot = telegram.Bot(token=bot_token)
    img_path = create_call_image(token['name'], token['mcap'], token['mcap'])
    
    caption = f"🔥 IFEYSYCO GEM 🔥\n\n${token['name']} | {token['chain'].upper()}\nMC: ${token['mcap']:,}\nLiq: ${token['liq']:,}\n\nContract:\n`{token['address']}`\n\nChart: {token['url']}\n\nBot: @ifeysycoai"
    await bot.send_photo(chat_id=channel, photo=open(img_path,'rb'), caption=caption, parse_mode='Markdown')
