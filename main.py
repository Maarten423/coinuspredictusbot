from flask import Flask, request
import logging
logging.basicConfig(level=logging.INFO)

import requests
import os
from forecast import generate_forecast  # Zorg dat deze module goed is ingevuld

app = Flask(__name__)

TOKEN = "7337750294:AAFgOM3X-e5jdmxAfv2D3cT2bbvprR3RyU4"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

@app.route("/", methods=["GET"])
def index():
    return "CoinusPredictusBot is actief!"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
logging.info(f"Ontvangen data: {data}")

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"].strip().lower()

        if "check" in text:
            forecast_text = generate_forecast()
            antwoord = f"📊 Top Coins volgens analyse:\n\n{forecast_text}"
        else:
            antwoord = "🤖 Stuur 'check' voor een realtime forecast van de 10 beste coins."

        # Verstuur antwoord via Telegram
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": antwoord
        })

    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)



