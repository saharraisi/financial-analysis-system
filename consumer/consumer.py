from confluent_kafka import Consumer, KafkaError
import json

# Kafka configuration
conf = {
    'bootstrap.servers': "my-django-release-kafka:9092",
    'group.id': "stock-consumer-group",
    'auto.offset.reset': 'earliest',
}

# Create Consumer instance
consumer = Consumer(conf)

# Subscribe to the topic
consumer.subscribe(['stock_data'])

# Dictionary to hold the closing prices for each stock symbol
stock_data = {}

# The window size for the moving averages and RSI calculation
window_size = 14  # Common window size for RSI is 14 periods


def calculate_sma(prices, window):
    if len(prices) < window:
        return None
    return sum(prices[-window:]) / window


def calculate_ema(prices, window):
    if not prices:
        return None
    elif len(prices) < 2:
        return prices[0]  # EMA is the same as the price if only one price is available
    else:
        ema_previous = prices[-2]
        multiplier = 2 / (window + 1)
        return (prices[-1] - ema_previous) * multiplier + ema_previous


def calculate_rsi(prices, window):
    if len(prices) < window + 1:
        return None

    gains = [max(prices[i] - prices[i-1], 0) for i in range(1, len(prices))]
    losses = [max(prices[i-1] - prices[i], 0) for i in range(1, len(prices))]

    average_gain = sum(gains[-window:]) / window
    average_loss = sum(losses[-window:]) / window

    if average_loss == 0:
        return 100  # Prevent division by zero

    rs = average_gain / average_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def decide_action(sma, ema, rsi):
    action = "Hold"  # Default action is to hold
    if ema and sma:
        if ema > sma and rsi and rsi < 70:
            action = "Buy"
        elif ema < sma and rsi and rsi > 30:
            action = "Sell"
    elif rsi:
        if rsi < 30:
            action = "Buy"
        elif rsi > 70:
            action = "Sell"
    return action

import requests

# Dictionary to hold the last action for each stock symbol
last_actions = {}

def send_action_to_endpoint(stock_symbol, sma, ema, rsi, action):
    url = "http://django-service:8000/data/stock-status-update/"  # Replace with your actual endpoint
    data = {
        "stock_symbol": stock_symbol,
        "sma": sma,
        "ema": ema,
        "rsi": rsi,
        "action": action
    }
    try:
        response = requests.get(url, params=data)
        response.raise_for_status()
        print(f"Successfully sent action for {stock_symbol} to endpoint.")
    except requests.RequestException as e:
        print(f"Error sending action for {stock_symbol} to endpoint: {e}")

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break

        data = json.loads(msg.value().decode('utf-8'))
        stock_symbol = data.get('stock_symbol')
        closing_price = data.get('closing_price')

        if stock_symbol and closing_price is not None:
            if stock_symbol not in stock_data:
                stock_data[stock_symbol] = []
                last_actions[stock_symbol] = "Hold"  # Initialize last action as "Hold"

            stock_data[stock_symbol].append(closing_price)

            sma = calculate_sma(stock_data[stock_symbol], window_size)
            ema = calculate_ema(stock_data[stock_symbol], window_size)
            rsi = calculate_rsi(stock_data[stock_symbol], window_size)

            action = decide_action(sma, ema, rsi)

            if action != last_actions[stock_symbol]:
                print(f"Action for {stock_symbol} changed to {action}. Sending to endpoint.")
                send_action_to_endpoint(stock_symbol, sma, ema, rsi, action)
                last_actions[stock_symbol] = action
            else:
                print(f"No action change for {stock_symbol}. Last action was {action}.")

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
