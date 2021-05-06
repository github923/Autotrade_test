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

# macdo 양수 갯수 세기
def count_macdo_positive(ticker):
    df = macd_osc(ticker)
    macdo_positive_count = 0
    for x in range(200):
        if df['macdo'][x] >= 0:
            macdo_positive_count += 1
    return macdo_positive_count

# macd 양수중에 상위 50퍼 구하기
def rank_macdo_positive(ticker):
    df = macd_osc(ticker)
    macdo_positive_count = count_macdo_positive(ticker)
    macdo_positive_rank = df['macdo'].rank(method='first', ascending=False)
    macdo_positive_rank_top_50 = macdo_positive_rank <= macdo_positive_count*0.50
    df['macdo_positive_rank_top_50'] = df['macdo'] * macdo_positive_rank_top_50
    return df
    
# macdo 음수 갯수 세기
def count_macdo_negative(ticker):
    df = macd_osc(ticker)
    macdo_negative_count = 0
    for x in range(200):
        if df['macdo'][x] < 0:
            macdo_negative_count += 1
    return macdo_negative_count

# macd 음수중에 상위 50퍼 구하기
def rank_macdo_negative(ticker):
    df = macd_osc(ticker)
    macdo_negative_count = count_macdo_negative(ticker)
    macdo_negative_rank = df['macdo'].rank(method='first', ascending=True)
    macdo_negative_rank_top_50 = macdo_negative_rank <= macdo_negative_count*0.50
    df['macdo_negative_rank_top_50'] = df['macdo'] * macdo_negative_rank_top_50
    return df
    
def macdo_min13_in_rank(ticker):
    df = rank_macdo_negative(ticker)
    macdo_min13_in_rank = []
    for x in range(-13,0):
        macdo_min13_in_rank.append(df['macdo_negative_rank_top_50'][x])
    last13_smallest_num = min(macdo_min13_in_rank)

    if last13_smallest_num == 0:
        time.sleep(1)

    elif last13_smallest_num < 0:
        if last13_smallest_num*0.6 <= df['macdo'][-1] <= last13_smallest_num*0.5:
            krw = upbit.get_balance("KRW")
            if krw>35000:
#             if krw>5000:
                upbit.buy_market_order(ticker, 10000)
#                 upbit.buy_market_order(ticker, krw*0.9995)
                print("purchase")
                time.sleep(180)
    return 0
    
def macdo_max13_in_rank(ticker):
    df = rank_macdo_positive(ticker)
    
    macdo_max13_in_rank = []
    for x in range(-13,0):
        macdo_max13_in_rank.append(df['macdo_positive_rank_top_50'][x])
    last13_largest_num = max(macdo_max13_in_rank)

    if last13_largest_num == 0:
        time.sleep(1)

    elif last13_largest_num > 0:
        if last13_largest_num*0.4 <= df['macdo'][-1] <= last13_largest_num*0.7:    
            sell_num = float(upbit.get_chance(ticker)['ask_account']['balance'])
            coin_num = upbit.get_balance(ticker)
            coin_price = get_current_price(ticker)
            if coin_num*coin_price>5000:
                upbit.sell_market_order(ticker, sell_num)
                print("sell")
                time.sleep(180)
    return 0


    
    
def macd_trading(ticker):
    df = macd_osc(ticker)
    if df['macdo'][-1] < 0:
        macdo_min13_in_rank(ticker)
    
    elif df['macdo'][-1] > 0:
        macdo_max13_in_rank(ticker)
    return 0
    
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
    sell_num = float(upbit.get_chance(ticker)['ask_account']['balance'])
    while sell_num > 0:
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

    return 0


def find_macdo_good(ticker):
    df1 = macd_osc(ticker , 'minute1')
    df5 = macd_osc(ticker , 'minute5')
    df30 = macd_osc(ticker , 'minute30')
    df120 = macd_osc(ticker , 'minute120')
    df1_increasing = (df1['macdo'][-1] >= df1['macdo'][-2])
    df5_increasing = (df5['macdo'][-1] >= df5['macdo'][-2])
    df30_increasing = (df30['macdo'][-1] >= df30['macdo'][-2])
    df120_increasing = (df120['macdo'][-1] >= df120['macdo'][-2])
    return [df1_increasing,df5_increasing,df30_increasing]
    
def tickers():
    tickers = []
    ticker = pyupbit.get_tickers()
    for x in range(len(ticker)):
        if (ticker[x][:3] == "KRW"):
            tickers.append(ticker[x])
    return tickers

def good_tickers():
    try:
        for x in tickers():
            variable_macdo = find_macdo_good(x)
            if variable_macdo == [True,True,True]:
                print(x)
        print('end')
    except:
        pass
def random_good_tickers():
    list = []
    while len(list) == 0:
        random_ticker = random.choice(tickers())
        if find_macdo_good(random_ticker) == [True,True,True]:
            list.append(random_ticker)
    return list[0]

while 1:
    min1('KRW-DOGE')
