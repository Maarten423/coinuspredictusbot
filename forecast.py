import requests
import logging
import os

def get_bitvavo_tickers():
    url = "https://api.bitvavo.com/v2/market/ticker/24h"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        tickers = response.json()
        logging.info(f"Aantal tickers ontvangen: {len(tickers)}")
        return tickers
    except Exception as e:
        logging.error(f"Fout bij ophalen tickers: {e}")
        return []

def score_coin(ticker):
    try:
        volume = float(ticker.get("volume", 0))
        price_change = float(ticker.get("priceChangePercentage", 0))

        if volume < 500_000:
            return 0

        score = price_change * (volume / 1_000_000)
        return round(score, 2)
    except Exception as e:
        logging.error(f"Fout bij score-berekening voor {ticker.get('market', 'onbekend')}: {e}")
        return 0

def generate_forecast():
    logging.info("Forecast gestart")
    tickers = get_bitvavo_tickers()

    if not tickers:
        return "⚠️ Geen data beschikbaar van Bitvavo."

    scores = []
    for ticker in tickers:
        score = score_coin(ticker)
        if score > 0:
            scores.append({
                "coin": ticker["market"].split("-")[0],
                "score": score,
                "volume": ticker["volume"],
                "change": ticker["priceChangePercentage"]
            })

    top_coins = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
    logging.info(f"Top 10 coins: {[c['coin'] for c in top_coins]}")

    if not top_coins:
        return "⚠️ Geen bruikbare coins gevonden."

    resultaat = ""
    for i, coin in enumerate(top_coins, 1):
        resultaat += (f"{i}. {coin['coin']}: ⭐️ Score: {coin['score']} | 📈 {coin['change']}% | 💰 Volume: €{round(float(coin['volume'])):,}\n")

    return resultaat
