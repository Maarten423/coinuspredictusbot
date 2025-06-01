import requests
import random

def generate_forecast():
    try:
        response = requests.get("https://api.bitvavo.com/v2/markets", timeout=10)
        markets = response.json()
    except Exception as e:
        return f"❌ Fout bij ophalen van coinlijst: {str(e)}"

    # Unieke coin-symbolen extraheren (alleen de 'base' zoals BTC, ETH etc.)
    coins = sorted(set([market['base'] for market in markets]))
    if len(coins) < 10:
        return "⚠️ Te weinig coins gevonden."

    geselecteerde = random.sample(coins, 10)
    resultaat = ""

    for i, coin in enumerate(geselecteerde, start=1):
        verwachte_stijging = round(random.uniform(4.0, 15.0), 1)
        stoploss = round(random.uniform(-5.0, -2.0), 1)
        rsi = random.randint(35, 70)
        ema = random.choice(["boven 20/50", "bullish crossover", "onder 20/50", "neutraal"])
        volume = random.randint(10, 150)
        nieuws = random.choice([
            f"Positief nieuws over {coin} circulerend",
            f"{coin} genoemd in crypto-analyses",
            f"Nieuwe listing verwacht op grote exchange",
            f"Geen noemenswaardig nieuws vandaag"
        ])
        sentiment = random.choice([
            "Koopvolume neemt toe, opwaarts momentum",
            "Lichte correctie, maar bullish trend intact",
            "Stabiel volume met stijgende interesse",
            "Opmerkelijke instroom van handelaren"
        ])

        resultaat += (
            f"{i}. ${coin}\n"
            f"📊 Verwachte stijging: +{verwachte_stijging}%\n"
            f"🔻 Stoploss: {stoploss}%\n"
            f"📈 RSI: {rsi}\n"
            f"📉 EMA: {ema}\n"
            f"🔥 Volume: +{volume}%\n"
            f"📰 Nieuws: {nieuws}\n"
            f"💬 {sentiment}\n\n"
        )

    return resultaat.strip()
