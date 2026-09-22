def is_good_gem(token):
    return token['mcap'] < 500000 and token['liq'] > 3000
