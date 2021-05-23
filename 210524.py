import time
import datetime
import pyupbit
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

access = "jXmymUVzgyJnixtTcYPfP7axp5YKpceWqBxVBplY"
secret = "Pc1YbwzPgJxVzwPYF9fPkenfqt3pKi50geoxLruq"


# 로그인
upbit = pyupbit.Upbit(access, secret)

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

def chart(ticker, interval):
    df = pyupbit.get_ohlcv(ticker, interval, count = '200')
    ma20 = df['close'].rolling(window=15).mean()
    df['ma20'] = ma20
    return df
    
def tickers():
    tickers = []
    ticker = pyupbit.get_tickers()
    for x in range(len(ticker)):
        if (ticker[x][:3] == "KRW"):
            tickers.append(ticker[x])
    return tickers

def ticker_unit(ticker):
    price = pyupbit.get_ohlcv(ticker)['close'][-1]
    if price < 10:
        unit = 0.01
    elif price < 100:
        unit = 0.1
    elif price < 1000:
        unit = 1
    elif price < 10000:
        unit = 5
    elif price < 100000:
        unit = 10
    elif price < 500000:
        unit = 50
    elif price < 1000000:
        unit = 100
    elif price < 5000000:
        unit = 500
    elif price > 5000000:
        unit = 1000
    return unit


def find_good_ticker():
    tickers = tickers()
    good_ticker = []
    for ticker in tickers:
        chart1 = chart(ticker, 'minute1')['close']
        chart30 = chart(ticker, 'minute30')['close']
        time.sleep(0.05)
        if (chart30['close'][-1] > chart30['ma20'][-1]) & (chart30['ma20'][-1] > chart30['ma20'][-2]) & (chart1['close'][-1] > chart1['open'][-1])&(chart1['close'][-1] > chart1['ma20'][-1]):
            good_ticker.append(ticker)
            time.sleep(0.05)

    print(good_ticker)
    time.sleep(1)
    
    return good_ticker
    


buy_or_not = 0
while 1:
    krw = upbit.get_balance("KRW")
    if buy_or_not == 0:
        tickers = []
        ticker = pyupbit.get_tickers()
        for x in range(len(ticker)):
            if (ticker[x][:3] == "KRW"):
                tickers.append(ticker[x])
        good_ticker = []
        for ticker in tickers:
            chart1 = chart(ticker, 'minute1')
            chart30 = chart(ticker, 'minute30')
            time.sleep(0.05)
            if (chart30['close'][-1] > chart30['ma20'][-1]) & (chart30['ma20'][-1] > chart30['ma20'][-2]) & (chart1['close'][-1] > chart1['open'][-1])&(chart1['close'][-1] > chart1['ma20'][-1])&(chart1['high'][-1] >= chart1['high'][-2]):
                good_ticker.append(ticker)
                time.sleep(0.05)

        print(good_ticker)
        time.sleep(1)
        
        if len(good_ticker) > 0:
#             ticker_unit = ticker_unit(good_ticker[0])
#             upbit.buy_market_order(good_ticker[0], 10000)
            print("purchase : ",good_ticker[0])
            buy_or_not = 1
            print(get_current_price(good_ticker[0]))
            print(time.strftime('%H-%M-%S', time.localtime(time.time())))
            time.sleep(1)
        else:
            print('good_ticker length is 0')
            print(time.strftime('%H-%M-%S', time.localtime(time.time())))
            pass

    elif buy_or_not == 1:
        if len(good_ticker) > 0:
            chart1 = chart(good_ticker[0], 'minute1')
            chart30 = chart(good_ticker[0], 'minute30')
            if chart1['close'][-1] <= max(chart1['high'][-1],chart1['high'][-2])*0.973:
                sell_num = float(upbit.get_chance(good_ticker[0])['ask_account']['balance'])
    #             upbit.sell_market_order(good_ticker[0], sell_num)
                print("high to minus 2.7% : ",good_ticker[0])
                buy_or_not = 0
                print(get_current_price(good_ticker[0]))
                print(time.strftime('%H-%M-%S', time.localtime(time.time())))
                time.sleep(1)

            elif upbit.get_avg_buy_price(good_ticker[0])*0.99 > get_current_price(good_ticker[0]):
                sell_num = float(upbit.get_chance(good_ticker[0])['ask_account']['balance'])
    #             upbit.sell_market_order(good_ticker[0], sell_num)
                print('stop loss minus 1% : ',good_ticker[0])
                buy_or_not = 0
                print(get_current_price(good_ticker[0]))
                print(time.strftime('%H-%M-%S', time.localtime(time.time())))
                time.sleep(1)

            elif chart30['close'][-1] < chart30['ma20'][-1]:
                coin_num = upbit.get_balance(good_ticker[0])
                coin_price = get_current_price(good_ticker[0])
                sell_num = float(upbit.get_chance(good_ticker[0])['ask_account']['balance'])
    #             upbit.sell_market_order(good_ticker[0], sell_num)
                print("sell : ",good_ticker[0])
                buy_or_not = 0
                print(get_current_price(good_ticker[0]))
                print(time.strftime('%H-%M-%S', time.localtime(time.time())))
                time.sleep(1)
        else:
            print('good_ticker length is 0')
            print(time.strftime('%H-%M-%S', time.localtime(time.time())))
            pass
