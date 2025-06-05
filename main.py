from flask import Flask, request
import requests
import os
import logging
from forecast import generate_forecast

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

@app.route("/", methods=["GET"])
def index():
    return "✅ CoinusPredictusBot is actief!"

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        logging.info(f"Ontvangen data: {data}")
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"]["text"].strip().lower()
           if "check" in text:
    logging.info("⚙️ Forecast wordt gegenereerd...")
    forecast_text = generate_forecast()
    antwoord = f"📊 Top Coins volgens analyse:\n\n{forecast_text}"
    logging.info(f"🔁 Antwoord dat wordt verstuurd: {antwoord}")

            else:
                antwoord = "🤖 Stuur 'check' voor een realtime forecast van de 10 beste coins."
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": antwoord})
    except Exception as e:
        logging.error(f"Fout in webhook-handler: {e}")
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
