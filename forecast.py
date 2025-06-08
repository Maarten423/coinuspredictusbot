import requests
import pandas as pd
import numpy as np
import logging
from pyti.relative_strength_index import relative_strength_index as rsi

logging.basicConfig(level=logging.INFO)

CRYPTOPANIC_API_KEY = "11e327720451865c51baabbdf9e24fcad10dd59f"
BITVAVO_BASE = "https://api.bitvavo.com/v2"

def fetch_bitvavo_markets():
    try:
        response = requests.get(f"{BITVAVO_BASE}/markets", timeout=10)
        response.raise_for_status()
        data = response.json()
        valid = [x for x in data if x["market"].endswith("-EUR")]
        logging.info(f"{len(valid)} markten opgehaald.")
        return valid
    except Exception as e:
        logging.error(f"Fout bij ophalen markten: {e}")
        return []

def fetch_ohlc(symbol):
    try:
        r = requests.get(f"{BITVAVO_BASE}/{symbol}/candles", params={"interval": "1h", "limit": 50}, timeout=10)
        r.raise_for_status()
        data = r.json()
        closes = [float(entry[4]) for entry in data if float(entry[4]) > 0]
        volumes = [float(entry[5]) for entry in data]
        return closes, volumes
    except Exception as e:
        logging.warning(f"Fout bij ophalen candles voor {symbol}: {e}")
        return [], []

def calculate_rsi(prices):
    if len(prices) < 14:
        return 50
    try:
        return round(rsi(prices, 14)[-1], 1)
    except:
        return 50

def calculate_ema(prices, window):
    return pd.Series(prices).ewm(span=window, adjust=False).mean().iloc[-1]

def fetch_news_sentiment(symbol):
    try:
        resp = requests.get(
            "https://cryptopanic.com/api/v1/posts/",
            params={
                "auth_token": CRYPTOPANIC_API_KEY,
                "currencies": symbol.lower(),
                "public": "true"
            },
            timeout=10
        )
        posts = resp.json().get("results", [])
        headlines = [post["title"] for post in posts if post.get("title")]
        return headlines[0][:100] + "..." if headlines else "Geen nieuws."
    except Exception as e:
        logging.warning(f"Fout bij nieuws {symbol}: {e}")
        return "Geen nieuws."

def score_coin(prices, volumes):
    if not prices or len(prices) < 2:
        return -999
    try:
        change = (prices[-1] - prices[-2]) / prices[-2] * 100
        ema20 = calculate_ema(prices, 20)
        ema50 = calculate_ema(prices, 50)
        rsi_val = calculate_rsi(prices)
        vol_change = (volumes[-1] - np.mean(volumes[:-1])) / np.mean(volumes[:-1]) * 100 if len(volumes) > 1 else 0
        score = change + (ema20 > ema50) * 5 + (50 - abs(50 - rsi_val)) + (vol_change / 10)
        return round(score, 2)
    except:
        return -999

def generate_forecast():
    logging.info("⚙️ Forecast gestart")
    tickers = fetch_bitvavo_markets()
    results = []

    for t in tickers:
        market = t['market']
        if not market.endswith("-EUR"):
            continue
        symbol = market.replace("-EUR", "")
        prices, volumes = fetch_ohlc(market)
        score = score_coin(prices, volumes)
        if score > -900:
            results.append({
                "symbol": symbol,
                "score": score,
                "prices": prices,
                "volumes": volumes
            })

    filtered = [
        r for r in results
        if r['prices'][-1] > r['prices'][-2]
        and calculate_ema(r['prices'], 20) > calculate_ema(r['prices'], 50)
        and 50 <= calculate_rsi(r['prices']) <= 80
    ]

    top_coins = sorted(filtered, key=lambda x: x["score"], reverse=True)[:10]
    logging.info(f"Top 10 coins: {[x['symbol'] for x in top_coins]}")

    if not top_coins:
        return "⚠️ Geen geschikte coins gevonden op basis van de huidige data."

    output = []
    for i, coin in enumerate(top_coins, 1):
        rsi_val = calculate_rsi(coin['prices'])
        ema20 = calculate_ema(coin['prices'], 20)
        ema50 = calculate_ema(coin['prices'], 50)
        vol_change = (coin['volumes'][-1] - np.mean(coin['volumes'][:-1])) / np.mean(coin['volumes'][:-1]) * 100 if len(coin['volumes']) > 1 else 0
        change = (coin['prices'][-1] - coin['prices'][-2]) / coin['prices'][-2] * 100 if len(coin['prices']) > 1 else 0
        news = fetch_news_sentiment(coin['symbol'])

        output.append(
            f"{i}. ${coin['symbol']}\n"
            f"📊 Verwachte stijging: {change:.1f}%\n"
            f"🔻 Stoploss: -{abs(change * 0.4):.1f}%\n"
            f"📈 RSI: {rsi_val}\n"
            f"📉 EMA: {'boven 20/50' if ema20 > ema50 else 'onder 20/50'}\n"
            f"🔥 Volume: {vol_change:.0f}%\n"
            f"🔖 Nieuws: {news}\n"
        )

    return "\n".join(output)
