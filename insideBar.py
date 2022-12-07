from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
import pandas as pd
from datetime import datetime, timedelta
import math
import time
import random
import threading

BASE_URL = "https://paper-api.alpaca.markets"
KEY_ID = "PK9GDJPUBRJVGQFYIDXW"
SECRET_KEY = "x7O11GYCcuJfxfps2jxeOh9PWxGxeFWEczLA4Rkw"
api = REST(key_id=KEY_ID, secret_key=SECRET_KEY,
           base_url="https://paper-api.alpaca.markets")


SYMBOLS = ["BTCUSD", "ETHUSD"]


def get_position(symbol):
    positions = api.list_positions()
    for p in positions:
        if p.symbol == symbol:
            return float(p.qty)
    return 0


def get_pause():
    now = datetime.now()
    next_min = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
    pause = math.ceil((next_min - now).seconds)
    print(f"Sleep for {pause}")
    return pause


def get_insideBar(bars):
    return bars.high[-2] > bars.high[-2] and bars.low[-1] > bars.low[-1]


def buy(ticker, bars):
    while True:
        quotes = api.get_quotes("AAPL", "2021-06-08",
                                "2021-06-08", limit=10).df
        avg = quotes.ask.rolling(10).mean()
        avg = round(avg, 2)
        if (avg > bars.high[-1]):
            notionalQTY = float(api.get_account().buying_power) * 0.05
            api.submit_order(ticker, notional=notionalQTY,
                             side='buy', time_in_force='gtc', trail_percent="2",
                             stop_loss=dict(
                                 stop_price=str(bars.low[-2]),
                                 limit_price=str(bars.low[-2])
                             ))
            print(f'Symbol: {ticker} / Side: BUY / Quantity: {notionalQTY}')

            return
        time.sleep(5)


while True:
    for ticker in SYMBOLS:
        notionalQTY = float(api.get_account().buying_power) * 0.05
        # GET DATA
        bars = api.get_crypto_bars("BTCUSD", TimeFrame.Minute).df
        bars = bars[bars.exchange == 'CBSE']
        should_buy = get_insideBar(bars)
        position = get_position(symbol=ticker)
        # CHECK POSITIONS
        if position == 0 and should_buy == True:
            # Start a thread
            t1 = threading.Thread(target=buy, args=(ticker, bars))

    time.sleep(get_pause())
    print("*"*20)
