# 자동매매 30분봉 진입 1분봉 절반매도 30분봉 절반매도 미완성

import time
import pyupbit
import datetime
import math

access = "jXmymUVzgyJnixtTcYPfP7axp5YKpceWqBxVBplY"
secret = "Pc1YbwzPgJxVzwPYF9fPkenfqt3pKi50geoxLruq"

def macd_osc_trading(ticker, interval):
    df = pyupbit.get_ohlcv(ticker, interval, count = '200')
    macd = df.close.ewm(span=12).mean() - df.close.ewm(span=26).mean() # 장기(26) EMA
    macds = macd.ewm(span=9).mean() # Signal
    macdo = macd - macds # Oscillato
    df['macdo'] = macdo
    df['macdo_is_positive'] = df['macdo'] > 0
    buy_or_sell = []
    for x in range(200):
        if x >= 1:
            if (df.iloc[x-1]['macdo_is_positive'] == 0) and (df.iloc[x]['macdo_is_positive'] == 0):
                buy_or_sell.append('no')
            elif (df.iloc[x-1]['macdo_is_positive'] == 1) and (df.iloc[x]['macdo_is_positive'] == 1):
                buy_or_sell.append('no')      
            elif (df.iloc[x-1]['macdo_is_positive'] == 0) and (df.iloc[x]['macdo_is_positive'] == 1):
                buy_or_sell.append('buy')
            elif (df.iloc[x-1]['macdo_is_positive'] == 1) and (df.iloc[x]['macdo_is_positive'] == 0):
                buy_or_sell.append('sell')
            else :
                pass
        else:
            buy_or_sell.append('first')
    df['buy_or_sell'] = buy_or_sell
    
    return df


def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute30", count=1)
    start_time = df.index[0]
    return start_time

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

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    Minimum_coin_selling_price = 5000/get_current_price('KRW-MED')
#     getbalance아님
    try:
        Immediate_purchase_price = pyupbit.get_orderbook(tickers="KRW-MED")[0]["orderbook_units"][0]["ask_price"]
        Number_of_coins = math.floor(get_balance("KRW") / Immediate_purchase_price)
        if macd_osc_trading(ticker = 'KRW-MED')['buy_or_sell'][-1] == 'buy':
            if get_balance("KRW") > 5000:
#                 즉시 구매가=판매 1호가
                Immediate_purchase_price = pyupbit.get_orderbook(tickers="KRW-MED")[0]["orderbook_units"][0]["ask_price"]
                upbit.buy_limit_order("KRW-MED", price = Immediate_purchase_price, volume = Number_of_coins)
                time = time.time()
                print(time, get_balance("KRW-MED"), "buying")
        elif macd_osc_trading(ticker = 'KRW-MED')['buy_or_sell'][-1] == 'sell':
            if get_balance('KRW-MED') > Minimum_coin_selling_price:
#                 즉시 판매가=구매 1호가
                Immediate_selling_price = pyupbit.get_orderbook(tickers="KRW-MED")[0]["orderbook_units"][0]["bid_price"]
                upbit.sell_limit_order("KRW-MED", price = Immediate_selling_price, volume = Number_of_coins)
                time = time.time()
                print(time, get_balance("KRW-MED"), "selling")
#         buy_or_sell 상태 반복노출
#         print(macd_osc_trading(ticker = 'KRW-MED')['buy_or_sell'][-1])
        time.sleep(1)
        
    except Exception as e:
        print(e)
        time.sleep(1)
