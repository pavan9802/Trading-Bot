from alpaca_trade_api.rest import REST, TimeFrame
import pandas as pd
from datetime import datetime, timedelta
import math
import time
import random

BASE_URL = "https://paper-api.alpaca.markets"
KEY_ID = "PK9E89NTGNYF6G7O5WX2"
SECRET_KEY = "8Y3O1kTiIQ8IrvoUhtybhBeod5CkXWpypphFw6Gk"
api = REST(key_id=KEY_ID, secret_key=SECRET_KEY,
           base_url="https://paper-api.alpaca.markets")


def get_position(symbol):
    positions = api.list_positions()
    for p in positions:
        if p.symbol == symbol:
            return float(p.qty)
    return 0


SYMBOLS = ["BTCUSD", "ETHUSD"]
while True:
    for ticker in SYMBOLS:
        # GET OUR CURRENT POSITION
        position = get_position(symbol=ticker)

        # SCIENTIFICALLY CHECK IF WE SHOULD BUY OR SELL
        gods_say_buy = random.choice([True, False])
        print(f"Holding: {position} / Gods: {gods_say_buy}")

        # CHECK IF WE SHOULD BUY
        if position == 0 and gods_say_buy == True:
            # WE BUY ONE BITCOIN
            print('The gods have spoken:')
            print(f'Symbol: {ticker} / Side: BUY / Quantity: 1')
            api.submit_order(ticker, qty=1, side='buy', time_in_force='gtc')
        # HECK IF WE SHOULD SELL
        elif position > 0 and gods_say_buy == False:
            # WE SELL ONE BITCOIN
            print('The gods have spoken:')
            print(f'Symbol: {ticker} / Side: SELL / Quantity: 1')
            api.submit_order(ticker, qty=1, side='sell', time_in_force='gtc')
        print('Lets wait for the gods to manifest again...')
    print("*"*20)
    time.sleep(2)
