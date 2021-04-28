import time
import pyupbit
import datetime

access = "jXmymUVzgyJnixtTcYPfP7axp5YKpceWqBxVBplY"
secret = "Pc1YbwzPgJxVzwPYF9fPkenfqt3pKi50geoxLruq"

def macd_osc_trading(ticker):
    df = pyupbit.get_ohlcv(ticker, interval='minute60', count = '200')
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
    
    return df['buy_or_sell'][-1]


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
    coin_sell_price = 5000/get_current_price('KRW-AXS')
    try:
        if macd_osc_trading(ticker = 'KRW-AXS') == 'buy':
            if target_price < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-AXS", krw*0.9995)
        elif macd_osc_trading(ticker = 'KRW-AXS') == 'sell':
            coin = get_balance("MBL")
            if coin > coin_sell_price:
                upbit.sell_market_order("KRW-AXS", coin*0.9995)
        # print(macd_osc_trading(ticker = 'KRW-AXS'))
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
