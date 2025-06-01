import requests
import pandas as pd
import numpy as np
import datetime
from pyti.relative_strength_index import relative_strength_index as rsi

CRYPTOPANIC_API_KEY = "11e327720451865c51baabbdf9e24fcad10dd59f"
BITVAVO_BASE = "https://api.bitvavo.com/v2"


def fetch_bitvavo_tickers():
    response = requests.get(f"{BITVAVO_BASE}/tickers")
    return response.json()


def fetch_ohlc(symbol):
    try:
        r = requests.get(
            f"{BITVAVO_BASE}/{symbol}/candles",
            params={"interval": "1h", "limit": 50}
        )
        data = r.json()
        closes = [float(entry[4]) for entry in data if float(entry[4]) > 0]
        volumes = [float(entry[5]) for entry in data]
        return closes, volumes
    except:
        return [], []


def calculate_ema(prices, window):
    return pd.Series(prices).ewm(span=window, adjust=False).mean().iloc[-1]


def calculate_rsi(prices):
    if len(prices) < 14:
        return 50
    return round(rsi(prices, 14)[-1], 1)


def fetch_news_sentiment(symbol):
    try:
        resp = requests.get(
            f"https://cryptopanic.com/api/v1/posts/",
            params={
                "auth_token": CRYPTOPANIC_API_KEY,
                "currencies": symbol.lower(),
                "public": "true"
            }
        )
        posts = resp.json().get("results", [])
        headlines = [post["title"] for post in posts if post.get("title")]
        if not headlines:
            return "Geen nieuws."
        return headlines[0][:100] + ("..." if len(headlines[0]) > 100 else "")
    except:
        return "Geen nieuws."


def score_coin(prices, volumes):
    if not prices:
        return -999
    change = (prices[-1] - prices[-2]) / prices[-2] * 100 if prices[-2] else 0
    ema20 = calculate_ema(prices, 20)
    ema50 = calculate_ema(prices, 50)
    rsi_val = calculate_rsi(prices)
    vol_change = (volumes[-1] - np.mean(volumes[:-1])) / np.mean(volumes[:-1]) * 100 if len(volumes) > 1 else 0
    score = change + (ema20 > ema50) * 5 + (50 - abs(50 - rsi_val)) + (vol_change / 10)
    return round(score, 2)


def generate_forecast():
    tickers = fetch_bitvavo_tickers()
    ranked = []
    for ticker in tickers:
        symbol = ticker['market'].replace("-EUR", "")
        prices, volumes = fetch_ohlc(ticker['market'])
        score = score_coin(prices, volumes)
        ranked.append({"symbol": symbol, "score": score, "prices": prices, "volumes": volumes})

    ranked = sorted([x for x in ranked if x['score'] > -900], key=lambda x: x['score'], reverse=True)[:10]

    output = []
    for idx, coin in enumerate(ranked, 1):
        rsi_val = calculate_rsi(coin['prices'])
        ema20 = calculate_ema(coin['prices'], 20)
        ema50 = calculate_ema(coin['prices'], 50)
        vol_change = (coin['volumes'][-1] - np.mean(coin['volumes'][:-1])) / np.mean(coin['volumes'][:-1]) * 100 if len(coin['volumes']) > 1 else 0
        change = (coin['prices'][-1] - coin['prices'][-2]) / coin['prices'][-2] * 100 if len(coin['prices']) > 1 else 0
        news = fetch_news_sentiment(coin['symbol'])

        output.append(
            f"{idx}. ${coin['symbol']}\n"
            f"📊 Verwachte stijging: {change:.1f}%\n"
            f"🔻 Stoploss: -{abs(change * 0.4):.1f}%\n"
            f"📈 RSI: {rsi_val}\n"
            f"📉 EMA: {'boven 20/50' if ema20 > ema50 else 'onder 20/50'}\n"
            f"🔥 Volume: {vol_change:.0f}%\n"
            f"📰 Nieuws: {news}\n"
            f"💬 Analyse: {'Bullish trend' if ema20 > ema50 else 'Afwachtend'} bij volume van {vol_change:.0f}%\n"
        )

    return "\n".join(output)

