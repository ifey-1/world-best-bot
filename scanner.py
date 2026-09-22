import requests
from filters import is_valid_gem

def scan_tokens():
    gems = []
    for chain in ['solana', 'base']:
        try:
            url = f"https://api.dexscreener.com/latest/dex/search/?q={chain}"
            r = requests.get(url, timeout=10).json()
            for pair in r.get('pairs', [])[:40]:
                if pair.get('chainId') != chain:
                    continue
                token = {
                    'name': pair['baseToken']['symbol'],
                    'address': pair['baseToken']['address'],
                    'mcap': int(pair.get('fdv',0) or 0),
                    'liq': int(pair.get('liquidity',{}).get('usd',0) or 0),
                    'vol': int(pair.get('volume',{}).get('m5',0) or 0),
                    'chain': chain,
                    'url': pair.get('url','')
                }
                if is_valid_gem(token):
                    gems.append(token)
        except Exception as e:
            print(f"Scan error {e}")
    return gems
