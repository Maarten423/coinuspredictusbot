import requests
import datetime
from cryptopanic import get_news_sentiment
from bitvavo import get_bitvavo_data
from indicators import calculate_rsi, calculate_ema, analyze_volume


def generate_forecast():
    coins = get_bitvavo_data()
    scored = []

    for coin in coins:
        try:
            rsi = calculate_rsi(coin['symbol'])
            ema = calculate_ema(coin['symbol'])
            volume_change = analyze_volume(coin['symbol'])
            news_score, top_news = get_news_sentiment(coin['symbol'])

            # Score opbouwen
            score = 0
            score += max(0, (50 - abs(50 - rsi))) / 10  # RSI-score
            score += 2 if ema == 'bullish' else 0
            score += min(volume_change / 10, 2)  # Volume-score max 2
            score += news_score  # Nieuws sentiment score

            scored.append({
                "symbol": coin['symbol'],
                "score": round(score, 2),
                "rsi": rsi,
                "ema": ema,
                "volume": volume_change,
                "news": top_news,
                "expected_gain": f"+{round(score * 1.5, 1)}%",
                "stoploss": f"-{round(score * 0.6, 1)}%",
            })
        except Exception as e:
            print(f"Fout bij coin {coin['symbol']}: {e}")

    top = sorted(scored, key=lambda x: x['score'], reverse=True)[:10]

    # Output formatteren
    message = "\ud83d\udcca Top 10 Coins volgens prijsverwachting komende 24 uur:\n\n"
    for i, coin in enumerate(top, start=1):
        message += (
            f"{i}. ${coin['symbol']}\n"
            f"\ud83d\udcca Verwachte stijging: {coin['expected_gain']}\n"
            f"\ud83d\udd3b Stoploss: {coin['stoploss']}\n"
            f"\ud83d\udcc8 RSI: {coin['rsi']}\n"
            f"\ud83d\udcc9 EMA: {coin['ema']}\n"
            f"\ud83d\udd25 Volume: +{coin['volume']}%\n"
            f"\ud83d\udcf0 Nieuws: {coin['news']}\n"
            f"\ud83d\udcac Analyse: Sterk momentum, score {coin['score']}\n\n"
        )

    return message.strip()
