def generate_crypto_price_endpoint(crypto:str="bitcoin",currency:str = "usd"):
    return f"https://api.coingecko.com/api/v3/simple/price?ids={crypto},ethereum&vs_currencies={currency}"