from PIL import Image, ImageDraw, ImageFont
import os

def create_call_image(token):
    img = Image.new('RGB', (800, 400), color=(10, 10, 30))
    draw = ImageDraw.Draw(img)
    
    draw.text((30, 30), f"${token['name']}", fill=(0, 255, 150), font=ImageFont.load_default())
    draw.text((30, 80), f"Chain: {token['chain'].upper()}", fill=(255, 255, 255), font=ImageFont.load_default())
    draw.text((30, 110), f"MC: ${token['mcap']:,}", fill=(255, 255, 255), font=ImageFont.load_default())
    draw.text((30, 140), f"Liq: ${token['liq']:,}", fill=(255, 255, 255), font=ImageFont.load_default())
    draw.text((30, 200), f"{token['address'][:20]}...", fill=(150, 150, 150), font=ImageFont.load_default())
    draw.text((30, 350), "IFEYSYCO WORLD BEST BOT", fill=(0, 255, 150), font=ImageFont.load_default())
    
    path = "/tmp/call.png"
    img.save(path)
    return path
