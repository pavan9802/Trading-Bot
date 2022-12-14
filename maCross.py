from alpaca_trade_api.rest import REST, TimeFrame
import pandas as pd
from datetime import datetime, timedelta
import math
import time


BASE_URL = "https://paper-api.alpaca.markets"
KEY_ID = "PK9GDJPUBRJVGQFYIDXW"
SECRET_KEY = "x7O11GYCcuJfxfps2jxeOh9PWxGxeFWEczLA4Rkw"
api = REST(key_id=KEY_ID, secret_key=SECRET_KEY,
           base_url="https://paper-api.alpaca.markets")


SMA_FAST = 12
SMA_SLOW = 24


def get_position(symbol):
    positions = api.list_positions()
    for p in positions:
        if p.symbol == symbol:
            print(p.qty)
            return float(p.qty)
    return 0

# Description is given in the article


def get_pause():
    now = datetime.now()
    next_min = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
    pause = math.ceil((next_min - now).seconds)
    print(f"Sleep for {pause}")
    return pause

# Same as the function in the random version


# Returns a series with the moving average
def get_sma(series, periods):
    return series.rolling(periods).mean()

# Checks wether we should buy (fast ma > slow ma)


def get_signal(fast, slow):
    print(f"Fast {fast[-1]}  /  Slow: {slow[-1]}")
    return fast[-1] > slow[-1]

# Get up-to-date 1 minute data from Alpaca and add the moving averages


def get_bars(symbol, stock):
    if stock:
        bars = api.get_bars(symbol, TimeFrame.Minute).df
        bars[f'sma_fast'] = get_sma(bars.close, SMA_FAST)
        bars[f'sma_slow'] = get_sma(bars.close, SMA_SLOW)
    else:
        bars = api.get_crypto_bars(symbol, TimeFrame.Minute).df
        bars = bars[bars.exchange == 'CBSE']
        bars[f'sma_fast'] = get_sma(bars.close, SMA_FAST)
        bars[f'sma_slow'] = get_sma(bars.close, SMA_SLOW)
    return bars


def buy_stocks(SYMBOLS):
    for ticker in SYMBOLS:
        notionalQTY = float(api.get_account().buying_power) * 0.05
        # GET DATA
        bars = get_bars(symbol=ticker, stock=True)
        # CHECK POSITIONS
        position = get_position(symbol=ticker)

        should_buy = get_signal(bars.sma_fast, bars.sma_slow)
        print(f"Position: {position} / Should Buy: {should_buy}")
        if position == 0 and should_buy == True:
            # WE BUY ONE BITCOIN
            api.submit_order(ticker, notional=notionalQTY,
                             side='buy', time_in_force='day')
            print(f'Symbol: {ticker} / Side: BUY / Quantity: {notionalQTY}')
        elif position > 0 and should_buy == False:
            # WE SELL ONE BITCOIN
            api.submit_order(ticker, qty=position,
                             side='sell', time_in_force='day')
            print(f'Symbol: {ticker} / Side: SELL / Quantity: {position}')
        time.sleep(.01)
        print()


def buy_crypto(SYMBOLS):
    for ticker in SYMBOLS:
        notionalQTY = float(api.get_account().buying_power) * 0.05
        # GET DATA
        bars = get_bars(symbol=ticker, stock=False)
        # CHECK POSITIONS
        position = get_position(ticker)

        should_buy = get_signal(bars.sma_fast, bars.sma_slow)
        print(f"Position: {position} / Should Buy {ticker}: {should_buy}")
        if position == 0 and should_buy == True:
            # WE BUY ONE BITCOIN
            api.submit_order(ticker, notional=notionalQTY,
                             side='buy', time_in_force='gtc')
            print(f'Symbol: {ticker} / Side: BUY / Quantity: {notionalQTY}')
        elif position > 0 and should_buy == False:
            # WE SELL ONE BITCOIN
            api.submit_order(ticker, qty=position,
                             side='sell', time_in_force='gtc')
            print(f'Symbol: {ticker} / Side: SELL / Quantity: {position}')
        time.sleep(.01)

        print()


while True:
    now = datetime.now()

    if float(now.strftime("%H")) == 15 and float(now.strftime("%M")) == 59:
        SYMBOLS = ["BTCUSD", "ETHUSD"]
        buy_crypto(SYMBOLS)

    elif float(now.strftime("%H")) >= 16:
        SYMBOLS = ["BTCUSD", "ETHUSD"]
        buy_crypto(SYMBOLS)

    else:
        SYMBOLS = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "JNJ", "V", "WMT", "JPM",
                   "NVDA", "MA", "META", "BAC", "CSCO", "SHEL", "ORCL", "MCD", "UPS", "MS", "NFLX", "QCOM", "GS"]
        buy_stocks(SYMBOLS)

    time.sleep(get_pause())
    print("*"*20)
