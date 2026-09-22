from PIL import Image, ImageDraw
def create_call_image(symbol, entry, now):
    img = Image.new('RGB', (1080, 1080), (18,18,18))
    d = ImageDraw.Draw(img)
    d.rectangle([0,0,1080,150], fill=(0,255,100))
    d.text((40,40), f"${symbol}", fill=(0,0,0))
    d.text((40,250), f"Entry MC: ${entry:,}", fill=(255,255,255))
    d.text((40,400), f"Target: 4X - 10X", fill=(0,255,100))
    d.text((40,950), "IFEYSYCO AI V9", fill=(100,100,100))
    p = f"/tmp/{symbol}.png"
    img.save(p)
    return p
