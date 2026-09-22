def is_valid_gem(token):
    mcap = token.get('mcap', 0)
    liq = token.get('liq', 0)
    vol = token.get('vol', 0)
    if not (8000 <= mcap <= 25000):
        return False
    if liq < 3000:
        return False
    if vol < 500:
        return False
    return True
