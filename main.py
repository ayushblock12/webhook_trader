from flask import Flask, request
from pybit.unified_trading import HTTP
import threading

app = Flask(__name__)

# Your Bybit API keys
api_key = "P95IalDQwSpUFZvUTQ51US1ovWfSRhAuYVTg"
api_secret = "red36cu3AaIIxEDXUO"

session = HTTP(api_key=api_key, api_secret=api_secret)

# Global flag to prevent duplicate positions
position_open = False

@app.route('/webhook', methods=['POST'])
def webhook():
    global position_open

    if position_open:
        return {"status": "Position already open"}

    data = request.json
    if data['passphrase'] != 'your_secret_passphrase':
        return {"error": "Invalid passphrase"}, 401

    # Example: Get current SOL price
    symbol = "SOLUSDT"
    ticker = session.get_ticker(symbol=symbol)["result"]["list"][0]
    current_price = float(ticker["lastPrice"])

    # Position settings
    leverage = 60
    margin = 3
    position_value = margin * leverage
    qty = round(position_value / current_price, 3)

    # Set TP and SL
    take_profit = round(current_price - 1, 2)
    stop_loss = round(current_price + 2, 2)

    try:
        session.place_order(
            category="linear",
            symbol=symbol,
            side="Sell",
            order_type="Market",
            qty=qty,
            time_in_force="GoodTillCancel",
            take_profit=take_profit,
            stop_loss=stop_loss,
            reduce_only=False
        )
        position_open = True
        print(f"Opened short: {qty} SOL at {current_price} with TP: {take_profit}, SL: {stop_loss}")
        return {"status": "Short position opened"}

    except Exception as e:
        print("Order error:", e)
        return {"error": str(e)}, 500

@app.route('/reset', methods=['POST'])
def reset_position_flag():
    global position_open
    position_open = False
    return {"status": "Position flag reset"}

@app.route('/')
def home():
    return "Auto Short Trade Bot is running."

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)