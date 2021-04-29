import time
import pyupbit
import datetime

access = "jXmymUVzgyJnixtTcYPfP7axp5YKpceWqBxVBplY"
secret = "Pc1YbwzPgJxVzwPYF9fPkenfqt3pKi50geoxLruq"


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


def macd_osc(ticker):
    df = pyupbit.get_ohlcv(ticker, interval='minute1', count = '200')
    macd = df.close.ewm(span=12).mean() - df.close.ewm(span=26).mean()
    macds = macd.ewm(span=9).mean()
    macdo = macd - macds
    df['macdo'] = macdo
    return df

def trading(ticker):
    df = macd_osc(ticker)
    df['macdo_is_positive'] = df['macdo'] > 0
    
    if (df.iloc[-2]['macdo_is_positive'] == 1):
            buy_or_sell = 1
    elif (df.iloc[-2]['macdo_is_positive'] == 0):
            buy_or_sell = 2
    else :
        pass

    return buy_or_sell



# 자동매매 시작
while True:
    try:
        if trading('KRW-DOGE') == 1:
            krw = get_balance("KRW")
            upbit.buy_market_order("KRW-DOGE", krw*0.9995)
            print("buy")
        elif trading('KRW-DOGE') == 2:
            coin = get_balance("KRW-DOGE")
            upbit.sell_market_order("KRW-DOGE", coin*0.9995)
            print("sell")
        elif trading('KRW-DOGE') == 0:
            print('no')
        else :
            pass
        print(macd_osc('KRW-DOGE').iloc[-1]['macdo'])
        time.sleep(1)
        
    except Exception as e:
        print(e)
        time.sleep(1)
