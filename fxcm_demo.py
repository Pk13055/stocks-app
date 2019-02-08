# -*- coding: utf-8 -*-
"""
Demo Strategy implemented on FXCM API

@author: Mayank Rasu
"""

import fxcmpy
import numpy as np
import pandas as pd
from stocktrends import Renko
import statsmodels.api as sm
import time

#initiating API connection and defining trade parameters
TOKEN = "fbec83ba39862a5d80026e42eb08af5349a20761"
con = fxcmpy.fxcmpy(access_token = TOKEN, log_level = 'error', server='demo')
pos_size = 6
pairs = ['EUR/USD','GBP/USD','USD/CHF','AUD/USD','USD/CAD','EUR/GBP','AUD/NZD']
lmt = 0.0008

def standardize_ser(ser):
    """Function to standardize each column of a dataframe  """
    std_ser = (ser - ser.mean())/ser.std()
    return std_ser

def slope2(ser,n):
    "function to calculate the slope of n consecutive points on a plot"
    slopes = [i*0 for i in range(n)]
    for i in range(n,len(ser)):
        y = ser[i-n:i]
        x = np.array(range(n))
        y_zs = standardize_ser(y)
        x_zs = standardize_ser(x)
        model = sm.OLS(y_zs,x_zs)
        results = model.fit()
        slopes.append(results.params[-1])
        slope_angle = (np.rad2deg(np.arctan(np.array(slopes))))
    return np.array(slope_angle)

def ATR(DF,n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['High']-df['Low'])
    df['H-PC']=abs(df['High']-df['Close'].shift(1))
    df['L-PC']=abs(df['Low']-df['Close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    return df2.loc[:,['TR','ATR']]

def renko_bricks(DF):
    "function to calculate trends based on Renko"
    renko_df = DF.copy()
    renko_df.reset_index(inplace=True)
    renko_df.columns = ["date","open","high","low","close","volume"]
    renko = Renko(renko_df)
    renko.brick_size = 0.0008
    df = renko.get_bricks()
    return df

def renko_bar_single_candle(ser):
    "function to account for multiple renko bars in the same candle"
    for i in range(1,len(ser)):
        if ser[i]>0 and ser[i-1]>0:
            ser[i]+=ser[i-1]
        elif ser[i]<0 and ser[i-1]<0:
            ser[i]+=ser[i-1]

def trade_signal_df(df):
    #creating renko bars
    ohlc = df.copy()
    renko_df = renko_bricks(ohlc)
    renko_df["bar_num"] = np.where(renko_df["uptrend"]==True,1,np.where(renko_df["uptrend"]==False,-1,0))
    renko_bar_single_candle(renko_df["bar_num"])                
    renko_df.drop_duplicates(subset="date",keep="last",inplace=True)
    
    #Merging renko df with original ohlc df
    ohlc["date"] = ohlc.index
    ohlc_renko = ohlc.merge(renko_df.loc[:,["date","bar_num"]],how="outer",on="date")
    ohlc_renko["bar_num"].fillna(method='ffill',inplace=True)
    
    
    #Implementing 6EMA and MACD (6,20,14)
    ohlc_renko['macd_ema_fast'] = ohlc_renko['Close'].ewm(span=6,adjust=False,min_periods=1).mean()
    ohlc_renko['macd_ema_slow'] = ohlc_renko['Close'].ewm(span=20,adjust=False,min_periods=1).mean()
    ohlc_renko['macd'] = (ohlc_renko['macd_ema_fast'] - ohlc_renko['macd_ema_slow'])
    ohlc_renko['signal'] = ohlc_renko['macd'].ewm(span=14,adjust=False,min_periods=1).mean()
    
    
    #Implementing Force Index
    ohlc_renko['force_index14'] = ((ohlc_renko['Close'] - ohlc_renko['Close'].shift(1))*ohlc_renko['Volume']).ewm(span=14,adjust=False,min_periods=1).mean()
    
    #Identifying Trend in the data using Renko and MACD
    ohlc_renko['trend'] = np.where(ohlc_renko["bar_num"]>=2,1,
                          np.where(ohlc_renko["bar_num"]<=-2,-1,0))
    
    #Calculating slopes for relevant curves and trade signal
    ohlc_renko['slope_ema_fast'] = slope2(ohlc_renko['macd_ema_fast'],4)
    ohlc_renko['slope_ema_slow'] = slope2(ohlc_renko['macd_ema_slow'],4)
    ohlc_renko['slope_force_index'] = slope2(ohlc_renko['force_index14'],4)
    ohlc_renko['slope_macd'] = slope2(ohlc_renko['macd'],4)
    ohlc_renko["trade_signal"] = np.where((ohlc_renko['trend']==1)&(ohlc_renko['Close']>ohlc_renko['macd_ema_fast'])&
                                     (ohlc_renko['slope_ema_fast']>10)&(ohlc_renko['slope_ema_slow']>10)&
                                     (ohlc_renko['slope_ema_fast']>ohlc_renko['slope_ema_slow'])&
                                     (ohlc_renko['slope_macd']>10)&
                                     (ohlc_renko['slope_force_index']>10)&(ohlc_renko['macd']>ohlc_renko['signal'])&
                                     (ohlc_renko['macd'].shift(1)<ohlc_renko['signal'].shift(1))&
                                     (ohlc_renko['macd'].shift(2)<ohlc_renko['signal'].shift(2)),'buy',
                           np.where((ohlc_renko['trend']==-1)&(ohlc_renko['Close']<ohlc_renko['macd_ema_fast'])&
                                     (ohlc_renko['slope_ema_fast']<-10)&(ohlc_renko['slope_ema_slow']<-10)&
                                     (ohlc_renko['slope_ema_fast']<ohlc_renko['slope_ema_slow'])&
                                     (ohlc_renko['slope_macd']<-10)&
                                     (ohlc_renko['slope_force_index']<-10)&(ohlc_renko['macd']<ohlc_renko['signal'])&
                                     (ohlc_renko['macd'].shift(1)>ohlc_renko['signal'].shift(1))&
                                     (ohlc_renko['macd'].shift(2)>ohlc_renko['signal'].shift(2)),'sell',''))
    return [ohlc_renko["trade_signal"].tolist(),ohlc_renko["Close"].tolist()]

def main():
    for currency in pairs:
        data = con.get_candles(currency, period='m1', number=250)
        ohlc = data.iloc[:,[0,1,2,3,8]]
        ohlc.columns = ["Open","Close","High","Low","Volume"]
        trade_signal = trade_signal_df(ohlc)[0]
        trade_signal[:] = (value for value in trade_signal if value != '')
        open_pos = con.get_open_positions()
        open_pos_cur = open_pos[open_pos["currency"]==currency]
        pos_price = trade_signal_df(ohlc)[1][-1]
   
        if len(open_pos_cur)>0:
            if open_pos_cur["isBuy"].tolist()[0]==True:
                if open_pos_cur["close"].tolist()[0] > open_pos_cur["open"].tolist()[0] + 1.5*lmt:
                    trade_id = open_pos_cur["tradeId"].tolist()[0]
                    num = int((open_pos_cur["close"].tolist()[0] - open_pos_cur["open"].tolist()[0])/lmt)
                    sl = max(open_pos_cur["stop"].tolist()[0], open_pos_cur["open"].tolist()[0] + 1.5*lmt, open_pos_cur["open"].tolist()[0] + num*lmt)
                    con.change_trade_stop_limit(trade_id, is_in_pips=False,is_stop=True, rate=sl,trailing_step=0)
                    print("stop loss revised to ",sl," for ",currency)
        elif len(open_pos_cur)>0:
            if open_pos_cur["isBuy"].tolist()[0]==False:
                if open_pos_cur["close"].tolist()[0] < open_pos_cur.tolist()["open"][0] - 1.5*lmt:
                    trade_id = open_pos_cur["tradeId"].tolist()[0]
                    num = int((open_pos_cur["open"].tolist()[0] - open_pos_cur["close"].tolist()[0])/lmt)
                    sl = min(open_pos_cur["stop"].tolist()[0], open_pos_cur["open"].tolist()[0] - 1.5*lmt, open_pos_cur["open"].tolist()[0] - num*lmt)
                    con.change_trade_stop_limit(trade_id, is_in_pips=False,is_stop=True, rate=sl,trailing_step=0)
                    print("stop loss revised to ",sl," for ",currency)
                    
        if len(trade_signal)>0 and trade_signal[-1] == 'buy':
            if len(open_pos_cur)==0:
                con.open_trade(symbol=currency,is_buy=True,amount=pos_size,is_in_pips=False,order_type='AtMarket',stop=pos_price-lmt,time_in_force='GTC')
                print("new long position initiated for ", currency)
            elif len(open_pos_cur)>0:
                if open_pos_cur["isBuy"].tolist()[0]==False:
                    con.close_all_for_symbol(currency)
                    print("Existing short position closed for ", currency)
                    con.open_trade(symbol=currency,is_buy=True,amount=pos_size,is_in_pips=False,order_type='AtMarket',stop=pos_price-lmt,time_in_force='GTC')
                    print("new long position initiated for ", currency)
                
        if len(trade_signal)>0 and trade_signal[-1] == 'sell':
            if len(open_pos_cur)==0:
                con.open_trade(symbol=currency,is_buy=False,amount=pos_size,is_in_pips=False,order_type='AtMarket',stop=pos_price+lmt,time_in_force='GTC')
                print("new short position initiated for ", currency)
            elif len(open_pos_cur)>0:
                if open_pos_cur["isBuy"].tolist()[0]==True:
                    con.close_all_for_symbol(currency)
                    print("Existing long position closed for ", currency)
                    con.open_trade(symbol=currency,is_buy=False,amount=pos_size,is_in_pips=False,order_type='AtMarket',stop=pos_price+lmt,time_in_force='GTC')
                    print("new short position initiated for ", currency)


# Continuous execution        
starttime=time.time()
timeout = time.time() + 60*60*24  # 60 seconds times 60 meaning the script will run for 1 hr
while time.time() <= timeout:
    try:
        time.sleep(1)
        main()
        time.sleep(60 - ((time.time() - starttime) % 60.0)) # 1 minute interval between each new execution
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        exit()
        
        
"""
def main():
    for currency in pairs:
        data = con.get_candles(currency, period='m1', number=250)
        ohlc = data.iloc[:,[0,1,2,3,8]]
        ohlc.columns = ["Open","Close","High","Low","Volume"]
        trade_signal = trade_signal_df(ohlc)[0]
        trade_signal[:] = (value for value in trade_signal if value != '')
        open_pos = con.get_open_positions()
        pos_price = trade_signal_df(ohlc)[1][-1]
        
        if len(open_pos)>0 and open_pos["isBuy"].tolist()[0]==True:
            if open_pos["close"].tolist()[0] > open_pos["open"].tolist()[0] + 1.5*lmt:
                trade_id = open_pos["tradeId"].tolist()[0]
                num = int((open_pos["close"].tolist()[0] - open_pos["open"].tolist()[0])/lmt)
                sl = max(open_pos["stop"].tolist()[0], open_pos["open"].tolist()[0] + 1.5*lmt,open_pos["open"].tolist()[0] + num*lmt)
                con.change_trade_stop_limit(trade_id, is_in_pips=False,is_stop=True, rate=sl,trailing_step=0)
        elif len(open_pos)>0 and open_pos["isBuy"].tolist()[0]==False:
            if open_pos["close"].tolist()[0] < open_pos["open"].tolist()[0] - 1.5*lmt:
                trade_id = open_pos["tradeId"].tolist()[0]
                num = int((open_pos["open"].tolist()[0] - open_pos["close"].tolist()[0])/lmt)
                sl = min(open_pos["stop"].tolist()[0], open_pos["open"].tolist()[0] - 1.5*lmt,open_pos["open"].tolist()[0] - num*lmt)
                con.change_trade_stop_limit(trade_id, is_in_pips=False,is_stop=True, rate=sl,trailing_step=0)
        
        if len(trade_signal)>0 and trade_signal[-1] == 'buy':
            if len(open_pos)==0:
                con.open_trade(symbol=currency,is_buy=True,amount=pos_size,is_in_pips=False,order_type='AtMarket',stop=pos_price-lmt,time_in_force='GTC')
            elif len(open_pos)>0 and open_pos["currency"].tolist()[0]==currency and open_pos["isBuy"].tolist()[0]==False:
                con.close_all_for_symbol(currency)
                con.open_trade(symbol=currency,is_buy=True,amount=pos_size,is_in_pips=False,order_type='AtMarket',stop=pos_price-lmt,time_in_force='GTC')
                
        if len(trade_signal)>0 and trade_signal[-1] == 'sell':
            if len(open_pos)==0:
                con.open_trade(symbol=currency,is_buy=False,amount=pos_size,is_in_pips=False,order_type='AtMarket',stop=pos_price+lmt,time_in_force='GTC')
            elif len(open_pos)>0 and open_pos["currency"].tolist()[0]==currency and open_pos["isBuy"].tolist()[0]==True:
                con.close_all_for_symbol(currency)
                con.open_trade(symbol=currency,is_buy=False,amount=pos_size,is_in_pips=False,order_type='AtMarket',stop=pos_price+lmt,time_in_force='GTC') 
"""