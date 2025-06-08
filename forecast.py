import requests
import logging
import time
import math
import os
from statistics import mean

CRYPTOPANIC_API_KEY = os.getenv("CRYPTOPANIC_API_KEY", "11e327720451865c51baabbdf9e24fcad10dd59f")

BITVAVO_URL = "https://api.bitvavo.com/v2/ticker/price"
RSI_URL = "https://api.taapi.io/rsi"
EMA_URL = "https://api.taapi.io/ema"

TAAPI_SECRET = os.getenv("TAAPI_SECRET", "demo")  # vervang door echte als beschikbaar

headers = {"accept": "application/json"}

def get_bitvavo_tickers():
    try:
        response = requests.get("https://api.bitvavo.com/v2/ticker/24h", headers=headers)
        response.raise_for_status()
        tickers = response.json()
        return tickers
    except Exception as e:
        logging.error(f"Fout bij ophalen tickers: {e}")
        return []

def get_rsi(symbol):
    try:
        response = requests.get(RSI_URL, params={
            "secret": TAAPI_SECRET,
            "exchange": "binance",
            "symbol": f"{symbol}/USDT",
            "interval": "1h"
        })
        return response.json().get("value", 50)
    except:
        return 50

def get_ema(symbol):
    try:
        fast = requests.get(EMA_URL, params={
            "secret": TAAPI_SECRET,
            "exchange": "binance",
            "symbol": f"{symbol}/USDT",
            "interval": "1h",
            "optInTimePeriod": 10
        }).json().get("value", 0)
        slow = requests.get(EMA_URL, params={
            "secret": TAAPI_SECRET,
            "exchange": "binance",
            "symbol": f"{symbol}/USDT",
            "interval": "1h",
            "optInTimePeriod": 50
        }).json().get("value", 0)
        return fast, slow
    except:
        return 0, 0

def get_news_score(symbol):
    try:
        response = requests.get("https://cryptopanic.com/api/v1/posts/", params={
            "auth_token": CRYPTOPANIC_API_KEY,
            "currencies": symbol.lower(),
            "filter": "hot",
            "public": "true"
        })
        posts = response.json().get("results", [])
        score = 0
        for post in posts:
            title = post.get("title", "").lower()
            if any(word in title for word in ["partnership", "launch", "adopt", "surge", "record"]):
                score += 5
            elif any(word in title for word in ["hack", "scam", "lawsuit", "ban", "exit"]):
                score -= 5
        return score
    except:
        return 0

def calculate_score(ticker):
    symbol = ticker["market"][:-4]  # verwijder "-EUR"
    try:
        price_change = float(ticker.get("priceChangePercentage24h", 0))
        volume = float(ticker.get("volume", 0))

        rsi = get_rsi(symbol)
        ema_fast, ema_slow = get_ema(symbol)
        news_score = get_news_score(symbol)

        rsi_score = max(0, min(100, rsi)) / 20 - 2.5
        ema_boost = 3 if ema_fast > ema_slow else -2
        volume_score = math.log(volume + 1) * 0.5

        score = price_change * 0.3 + rsi_score + ema_boost + volume_score + news_score
        return score
    except Exception as e:
        logging.warning(f"Kon score niet berekenen voor {symbol}: {e}")
        return -999

def generate_forecast():
    logging.info("Forecast gestart")
    tickers = get_bitvavo_tickers()
    logging.info(f"Aantal tickers ontvangen: {len(tickers)}")

    scored = []
    for ticker in tickers:
        if not ticker["market"].endswith("-EUR"):
            continue
        score = calculate_score(ticker)
        scored.append((ticker["market"], score))

    scored = sorted([s for s in scored if s[1] > -999], key=lambda x: x[1], reverse=True)[:10]

    if not scored:
        return "⚠️ Geen bruikbare coins gevonden."

    lines = [f"{i+1}. {name}: score {round(score, 2)}" for i, (name, score) in enumerate(scored)]
    return "\n".join(lines)
