# 세이브2
import time
import pyupbit
import datetime
import numpy as np
import pandas as pd
import random

access = "jXmymUVzgyJnixtTcYPfP7axp5YKpceWqBxVBplY"
secret = "Pc1YbwzPgJxVzwPYF9fPkenfqt3pKi50geoxLruq"


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]
        
def macd_osc(ticker,interval):
    df = pyupbit.get_ohlcv(ticker, interval, count = '200')
    macd = df['close'].ewm(span=12).mean() - df['close'].ewm(span=60).mean()
    macds = macd.ewm(span=10).mean()
    macdo = macd - macds
    df['macdo'] = macdo
    return df

def stop_loss(ticker):
    coin_num = upbit.get_balance(ticker)
    coin_price = get_current_price(ticker)
    if coin_num*coin_price>5000:
        if upbit.get_avg_buy_price(ticker)*0.993 > get_current_price(ticker):
            sell_num = float(upbit.get_chance(ticker)['ask_account']['balance'])
            upbit.sell_market_order(ticker, sell_num)
            print('stop loss')
    return 0
    
def min1(ticker):
    df1 = macd_osc(ticker, 'minute1')
    df5 = macd_osc(ticker, 'minute5')
    df30 = macd_osc(ticker, 'minute30')
    krw = upbit.get_balance("KRW")
    if krw>35000:
        if df30['macdo'][-1] > df30['macdo'][-2]:
            if df5['macdo'][-1] > df5['macdo'][-2]:
                if df1['macdo'][-1] > df1['macdo'][-2] > df1['macdo'][-3]:
                    upbit.buy_market_order(ticker, 10000)
                    print("purchase : ",ticker)
                    time.sleep(1)
    if krw<35000:
        if upbit.get_avg_buy_price(ticker)*0.99 > get_current_price(ticker):
            sell_num = float(upbit.get_chance(ticker)['ask_account']['balance'])
            upbit.sell_market_order(ticker, sell_num)
            print('stop loss : ',ticker)
            time.sleep(1)

        elif df1['macdo'][-1] < df1['macdo'][-2] < df1['macdo'][-3]:
            coin_num = upbit.get_balance(ticker)
            coin_price = get_current_price(ticker)
            sell_num = float(upbit.get_chance(ticker)['ask_account']['balance'])
            if coin_num*coin_price > 5000:
                upbit.sell_market_order(ticker, sell_num)
                print("sell : ",ticker)
                time.sleep(1)
        time.sleep(1)
    return 0

while 1:
    min1('KRW-DOGE')
