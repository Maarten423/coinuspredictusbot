import requests
import logging

# Logging
logging.basicConfig(level=logging.INFO)

def get_tickers():
    url = "https://api.bitvavo.com/v2/ticker/24h"
    try:
        response = requests.get(url)
        response.raise_for_status()
        tickers = response.json()
        logging.info(f"Aantal tickers ontvangen: {len(tickers)}")
        return tickers
    except requests.RequestException as e:
        logging.error(f"Fout bij ophalen tickers: {e}")
        return []



def get_market_data(symbols):
    market_data = {}
    chunk_size = 200
    for i in range(0, len(symbols), chunk_size):
        chunk = symbols[i:i + chunk_size]
        try:
            markets_string = ','.join(chunk)
            url = f"https://api.bitvavo.com/v2/markets?symbols={markets_string}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            for item in data:
                symbol = item.get('market')
                if symbol:
                    market_data[symbol] = item
        except Exception as e:
            logging.error(f"Fout bij ophalen market data voor batch {i}-{i+chunk_size}: {e}")
    return market_data

def calculate_score(ticker, market_info):
    try:
        price_change = float(ticker.get('priceChangePercentage24h', 0))
        volume = float(ticker.get('volume', 0))
        score = price_change * volume  # Simpele formule
        return score
    except:
        return 0

def generate_forecast():
    logging.info("Forecast gestart")
    tickers = get_tickers()
    if not tickers:
        return "⚠️ Geen data beschikbaar van Bitvavo."

    market_symbols = [t['market'] for t in tickers if 'market' in t]
    logging.info(f"Aantal markten ontvangen: {len(market_symbols)}")

    market_data = get_market_data(market_symbols)

    scored = []
    for ticker in tickers:
        symbol = ticker.get('market')
        if symbol in market_data:
            score = calculate_score(ticker, market_data[symbol])
            scored.append((symbol, score))

    top_coins = sorted(scored, key=lambda x: x[1], reverse=True)[:10]
    logging.info(f"Top 10 coins: {top_coins}")

    if not top_coins:
        return "⚠️ Geen sterke kandidaten gevonden."

    resultaat = []
    for i, (symbol, score) in enumerate(top_coins, start=1):
        resultaat.append(f"{i}. {symbol} – score: {round(score, 2)}")

    return "\n".join(resultaat)
