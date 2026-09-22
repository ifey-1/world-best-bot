import requests

def scan_tokens():
    gems = []
    try:
        # Scan Solana new pairs
        url = "https://api.dexscreener.com/latest/dex/search/?q=solana"
        r = requests.get(url, timeout=10).json()
        for p in r.get('pairs', [])[:10]:
            try:
                mcap = p.get('fdv', 0) or p.get('marketCap', 0) or 0
                liq = p.get('liquidity', {}).get('usd', 0) or 0
                if 5000 < mcap < 500000 and liq > 3000:
                    gems.append({
                        'name': p['baseToken']['symbol'],
                        'address': p['baseToken']['address'],
                        'chain': p['chainId'],
                        'mcap': int(mcap),
                        'liq': int(liq),
                        'url': p['url']
                    })
            except:
                continue
    except Exception as e:
        print(f"Scan error: {e}")
    return gems
