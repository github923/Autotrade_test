import time
import pyupbit
import datetime
import numpy as np
import pandas as pd

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

def RSI_trading(ticker):
    df = pyupbit.get_ohlcv(ticker, interval='minute1', count = '200')
    U = np.where(df.diff(1)['close'] > 0, df.diff(1)['close'], 0) 
    D = np.where(df.diff(1)['close'] < 0, df.diff(1)['close'] *(-1), 0) 
    AU = pd.DataFrame(U).rolling(window=5).mean() 
    AD = pd.DataFrame(D).rolling(window=50).mean() 
    RSI = AU.div(AD+AU) * 100 
    RSI_save = []
    for x in range(200):
        RSI_save.append(round(float(RSI.iloc[x]),4))
    df['RSI'] = RSI_save
    return df

def RSI_trading_df(ticker):    
    df = RSI_trading(ticker)
    
    RSI_max10 = []
    for x in range(9):
        RSI_max10.append('no')
    for x in range(10,201):
        maxs = df['RSI'][x-10:x].max()
        RSI_max10.append(maxs)
    df['RSI_max10'] = RSI_max10
    
    RSI_min10 = []
    for x in range(9):
        RSI_min10.append('no')
    for x in range(10,201):
        mins = df['RSI'][x-10:x].min()
        RSI_min10.append(mins)
    df['RSI_min10'] = RSI_min10
    return df



def buy_or_sell(ticker):
    df = macd_osc(ticker)
    df['macdo_is_positive'] = df['macdo'] > 0
    
    if (df.iloc[-1]['macdo_is_positive'] == 1):
        buy_or_sell = 1
    elif (df.iloc[-1]['macdo_is_positive'] == 0):
        buy_or_sell = 2
    else :
        buy_or_sell = 0
    return buy_or_sell
        
        
        
def macd_osc(ticker):
    df = pyupbit.get_ohlcv(ticker, interval='minute1', count = '200')
    macd = df.close.ewm(span=12).mean() - df.close.ewm(span=60).mean()
    macds = macd.ewm(span=10).mean()
    macdo = macd - macds
    df['macdo'] = macdo
    return df

def macd_osc_df(ticker):
    df = macd_osc(ticker)
    
    macdo_max10 = []
    for x in range(9):
        macdo_max10.append('no')
    for x in range(10,201):
        maxs = df['macdo'][x-10:x].max()
        macdo_max10.append(maxs)
    df['macdo_max10'] = macdo_max10

    macdo_min10 = []
    for x in range(9):
        macdo_min10.append('no')
    for x in range(10,201):
        mins = df['macdo'][x-10:x].min()
        macdo_min10.append(mins)
    df['macdo_min10'] = macdo_min10
    
#     macd 양수중에 상위 75퍼 구하기
    macdo_positive_count = 0
    for x in range(200):
        if df['macdo'][x] >= 0:
            macdo_positive_count += 1
    macdo_positive_rank = df['macdo'].rank(method='first', ascending=False)
    macdo_positive_rank_top_50 = macdo_positive_rank < macdo_positive_count*0.75
    df['macdo_positive_rank_top_50'] = df['macdo'] * macdo_positive_rank_top_50
    
#     macd 음수중에 하위 75퍼 구하기
    macdo_negative_count = 0
    for x in range(200):
        if df['macdo'][x] < 0:
            macdo_negative_count += 1
    macdo_negative_rank = df['macdo'].rank(method='first', ascending=True)
    macdo_negative_rank_top_50 = macdo_negative_rank < macdo_negative_count*0.75
    df['macdo_negative_rank_top_50'] = df['macdo'] * macdo_negative_rank_top_50
        
    
    return df



def trading(ticker):
    if buy_or_sell(ticker) == 1:
        krw = upbit.get_balance("KRW")
        if krw>5000:
            upbit.buy_market_order(ticker, krw*0.9995)
            print("buy")
            print('macdo',macd_osc(ticker).iloc[-1]['macdo'])
            time.sleep(120)
        else:
            print('buy__')
            print('macdo',macd_osc(ticker).iloc[-1]['macdo'])
    elif buy_or_sell(ticker) == 2:
        coin_num = upbit.get_balance(ticker)
        coin_price = get_current_price(ticker)
        if coin_num*coin_price>5000:
            upbit.sell_market_order(ticker, coin_num*0.9995)
            print("sell")
            print('macdo',macd_osc(ticker).iloc[-1]['macdo'])
            time.sleep(120)
        else:
            print('sell__')
            print('macdo',macd_osc(ticker).iloc[-1]['macdo'])
    elif buy_or_sell(ticker) == 0:
        print('no')
    else :
        pass
    time.sleep(1)

    
def macdo_min13_in_rank(ticker):
    df = macd_osc_df(ticker)
    
    macdo_min13_in_rank = []
    for x in range(-13,0):
        macdo_min13_in_rank.append(df['macdo_negative_rank_top_50'][x])
    last13_smallest_num = min(macdo_min13_in_rank)

    if last13_smallest_num == 0:
        time.sleep(1)

    elif last13_smallest_num < 0:
        if last13_smallest_num*0.5 <= df['macdo'][-1] <= last13_smallest_num*0.6:
            krw = upbit.get_balance("KRW")
            if krw>25000:
#             if krw>5000:
                upbit.buy_market_order(ticker, 10000)
#                 upbit.buy_market_order(ticker, krw*0.9995)
                print("buy")
                time.sleep(180)       
    else:
        pass
    
def macdo_max13_in_rank(ticker):
    df = macd_osc_df(ticker)
    
    macdo_max13_in_rank = []
    for x in range(-13,0):
        macdo_max13_in_rank.append(df['macdo_positive_rank_top_50'][x])
    last13_largest_num = max(macdo_max13_in_rank)

    if last13_largest_num == 0:
        time.sleep(1)

    elif last13_largest_num > 0:
        if last13_largest_num*0.65 <= df['macdo'][-1] <= last13_largest_num*0.7:    
            sell_num = float(upbit.get_chance(ticker)['ask_account']['balance'])
            coin_num = upbit.get_balance(ticker)
            coin_price = get_current_price(ticker)
            if coin_num*coin_price>5000:
                upbit.sell_market_order(ticker, sell_num)
                print("sell")
                time.sleep(180)       
    else:
        pass


    
    
def macd_trading(ticker):
    df = macd_osc_df(ticker)
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
    
    
while 1:
    macd_trading('KRW-BTT')
    stop_loss('KRW-BTT')
