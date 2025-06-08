import requests
import time
import logging

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

def get_scores(tickers):
    # Simpele mock score voor demo (vervang met echte berekening)
    scored = []
    for t in tickers:
        if "volume" in t and t.get("volume", 0):
            try:
                score = float(t["priceChange"]) / float(t["open"]) * 100
                scored.append({"market": t["market"], "score": round(score, 2)})
            except (KeyError, ValueError, ZeroDivisionError):
                continue
    return scored

def generate_forecast():
    logging.info("Forecast gestart")
    
    tickers = get_tickers()
    if not tickers:
        logging.warning("⚠️ Geen data beschikbaar van Bitvavo.")
        return "⚠️ Geen data beschikbaar van Bitvavo."

    scores = get_scores(tickers)
    if not scores:
        return "⚠️ Geen bruikbare coins gevonden."

    sorted_scores = sorted(scores, key=lambda x: x["score"], reverse=True)
    top10 = sorted_scores[:10]

    logging.info(f"Top 10 coins: {top10}")
    
    forecast_text = ""
    for coin in top10:
        forecast_text += f"{coin['market']}: {coin['score']}%\n"
    
    return forecast_text.strip()
