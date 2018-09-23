from upstox_api.api import Upstox, datetime, OHLCInterval, TransactionType, OrderType, ProductType, DurationType
import time
import os
import pandas as pd
import datetime as dt
import numpy as np

cwd = os.getcwd()

access_token = open(os.path.join(cwd,"access_token.txt"),'r').read()

config = {
	'apiKey': 'AAJ0Rx0qDu5TExtIOhEIH1od78siET7t6SuMiGsO',
	'accessToken': access_token
}

# Create the UpstoxAPI object bound to your API key
upstoxAPI = Upstox(config['apiKey'], config['accessToken'])

# get master contract for NSE EQ
upstoxAPI.get_master_contract('NSE_EQ')

# create an array of Nifty50 scrips
scrips = (
	"ACC",
	"ADANIPORTS", "AMBUJACEM", "ASIANPAINT",
	"AUROPHARMA", "AXISBANK", "BAJAJ-AUTO", "BANKBARODA",
	"BPCL", "BHARTIARTL", "INFRATEL", "BOSCHLTD",
	"CIPLA", "COALINDIA", "DRREDDY", "EICHERMOT",
	"GAIL", "HCLTECH", "HDFCBANK", "HEROMOTOCO",
	"HINDALCO", "HINDUNILVR", "HDFC", "ITC", "ICICIBANK",
	"IBULHSGFIN", "IOC", "INDUSINDBK", "INFY", "KOTAKBANK",
	"LT", "LUPIN", "M&M", "MARUTI", "NTPC", "ONGC",
	"POWERGRID", "RELIANCE", "SBIN", "SUNPHARMA",
	"TCS", "TATAMTRDVR", "TATAMOTORS", "TATAPOWER",
	"TATASTEEL", "TECHM", "ULTRACEMCO", "VEDL",
	"WIPRO", "YESBANK", "ZEEL"
)
capital = 7200

def placeOrder(symbol, exchange, side, quantity):
    exchange = "NSE_EQ"
    scrip = upstoxAPI.get_instrument_by_symbol(exchange, symbol)
    upstoxAPI.place_order(
		side,  # transaction_type
		scrip,  # instrument
		quantity,  # quantity
		OrderType.Market,  # order_type
		ProductType.Intraday,  # product_type
		0.0,  # price
		None,  # trigger_price
		0,  # disclosed_quantity
		DurationType.DAY,  # duration
		None,  # stop_loss
		None,  # square_off
		None  # trailing_ticks
	)
    
def slmOrder(symbol, exchange, side, quantity, trigger):
    exchange = "NSE_EQ"
    scrip = upstoxAPI.get_instrument_by_symbol(exchange, symbol)
    upstoxAPI.place_order(
		side,  # transaction_type
		scrip,  # instrument
		quantity,  # quantity
		OrderType.StopLossMarket,  # order_type
		ProductType.Intraday,  # product_type
		0.0,  # price
		trigger,  # trigger_price
		0,  # disclosed_quantity
		DurationType.DAY,  # duration
		None,  # stop_loss
		None,  # square_off
		None  # trailing_ticks
	)
    
def modifyOrder(order_id, trigger):
    upstoxAPI.modify_order(
		order_id,  # order_id
		None,  # quantity
		OrderType.StopLossMarket,  # order_type
		0.0,  # price
		trigger,  # trigger_price
		0,  # disclosed_quantity
	)

def fetchOHLC(scrip):
	return upstoxAPI.get_ohlc(scrip,OHLCInterval.Minute_5,dt.date.today()-dt.timedelta(15), dt.date.today())

def ATR(DF,n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['high']-df['low'])
    df['H-PC']=abs(df['high']-df['cp'].shift(1))
    df['L-PC']=abs(df['low']-df['cp'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    #df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    return df2.loc[:,['TR','ATR']]

def ADX(DF,n):
    "function to calculate ADX"
    df2 = DF.copy()
    df2['TR'] = ATR(df2,10)['TR'] #the parameter for ATR function does not matter because we only need TR
    df2['DMplus']=np.where((df2['high']-df2['high'].shift(1))>(df2['low'].shift(1)-df2['low']),df2['high']-df2['high'].shift(1),0)
    df2['DMplus']=np.where(df2['DMplus']<0,0,df2['DMplus'])
    df2['DMminus']=np.where((df2['low'].shift(1)-df2['low'])>(df2['high']-df2['high'].shift(1)),df2['low'].shift(1)-df2['low'],0)
    df2['DMminus']=np.where(df2['DMminus']<0,0,df2['DMminus'])
    TRn = []
    DMplusN = []
    DMminusN = []
    TR = df2['TR'].tolist()
    DMplus = df2['DMplus'].tolist()
    DMminus = df2['DMminus'].tolist()
    for i in range(len(df2)):
        if i < n:
            TRn.append(np.NaN)
            DMplusN.append(np.NaN)
            DMminusN.append(np.NaN)
        elif i == n:
            TRn.append(df2['TR'].rolling(n).sum().tolist()[n])
            DMplusN.append(df2['DMplus'].rolling(n).sum().tolist()[n])
            DMminusN.append(df2['DMminus'].rolling(n).sum().tolist()[n])
        elif i > n:
            TRn.append(TRn[i-1] - (TRn[i-1]/14) + TR[i])
            DMplusN.append(DMplusN[i-1] - (DMplusN[i-1]/14) + DMplus[i])
            DMminusN.append(DMminusN[i-1] - (DMminusN[i-1]/14) + DMminus[i])
    df2['TRn'] = np.array(TRn)
    df2['DMplusN'] = np.array(DMplusN)
    df2['DMminusN'] = np.array(DMminusN)
    df2['DIplusN']=100*(df2['DMplusN']/df2['TRn'])
    df2['DIminusN']=100*(df2['DMminusN']/df2['TRn'])
    df2['DIdiff']=abs(df2['DIplusN']-df2['DIminusN'])
    df2['DIsum']=df2['DIplusN']+df2['DIminusN']
    df2['DX']=100*(df2['DIdiff']/df2['DIsum'])
    ADX = []
    DX = df2['DX'].tolist()
    for j in range(len(df2)):
        if j < 2*n-1:
            ADX.append(np.NaN)
        elif j == 2*n-1:
            ADX.append(df2['DX'][j-n+1:j+1].mean())
        elif j > 2*n-1:
            ADX.append(((n-1)*ADX[j-1] + DX[j])/n)
    df2['ADX']=np.array(ADX)
    return df2['ADX']

def RSI(DF,n):
    "function to calculate RSI"
    df = DF.copy()
    df['pc']=df['cp'] - df['cp'].shift(1)
    df['gain']=np.where(df['pc']>=0,df['pc'],0)
    df['loss']=np.where(df['pc']<0,abs(df['pc']),0)
    avg_gain = []
    avg_loss = []
    gain = df['gain'].tolist()
    loss = df['loss'].tolist()
    for i in range(len(df)):
        if i < n:
            avg_gain.append(np.NaN)
            avg_loss.append(np.NaN)
        elif i == n:
            avg_gain.append(df['gain'].rolling(n).mean().tolist()[n])
            avg_loss.append(df['loss'].rolling(n).mean().tolist()[n])
        elif i > n:
            avg_gain.append(((n-1)*avg_gain[i-1] + gain[i])/n)
            avg_loss.append(((n-1)*avg_loss[i-1] + loss[i])/n)
    df['avg_gain']=np.array(avg_gain)
    df['avg_loss']=np.array(avg_loss)
    df['RS'] = df['avg_gain']/df['avg_loss']
    #df['RS']=((df['avg_gain'].shift(1)*13 + df['gain'].shift(1))/14)/((df['avg_loss'].shift(1)*13 + df['loss'].shift(1))/14)
    df['RSI'] = 100 - (100/(1+df['RS']))
    return df['RSI']

def main():
    global capital
    attempt = 0
    while attempt<10:
        try:
            pos_df = pd.DataFrame(upstoxAPI.get_positions())
            break
        except:
            print("can't get position...attempt =",attempt)
            attempt+=1
    while attempt<10:
        try:
            order_df = pd.DataFrame(upstoxAPI.get_order_history())
            break
        except:
            print("can't get order information...attempt =",attempt)
            attempt+=1
    for ticker in scrips:
        buy_status = False
        sell_status = False
        try:
            scrip = upstoxAPI.get_instrument_by_symbol('NSE_EQ', ticker)
            message = fetchOHLC(scrip)
            df = pd.DataFrame(message)
            df["timestamp"] = pd.to_datetime(df["timestamp"]/1000,unit='s')+ pd.Timedelta('05:30:00')
            df.set_index("timestamp",inplace=True)
            df["ADX_14"] = ADX(df,14)
            df["RSI_14"] = RSI(df,14)
            df['signal'] =np.where((df["ADX_14"]>25)&(df["RSI_14"]>60),1,
                            np.where((df["ADX_14"]>25)&(df["RSI_14"]<40),-1,0))
            quantity = int(capital/df["cp"][-1])
            if len(order_df)>0:
                ticker_orders = order_df[order_df["symbol"]==ticker]
                if len(ticker_orders)>0:
                    pending_df = ticker_orders[ticker_orders["status"]=="trigger pending"]
                    if len(pending_df)>0:
                        order_id = int(pending_df["order_id"].values[0])
            if len(pos_df)>0:
                pos = pos_df[pos_df["symbol"]==ticker]
                if len(pos)>0:
                    if (pos["buy_quantity"]-pos["sell_quantity"]).values[-1] >0:
                        buy_status = True
                        quantity = int((pos["buy_quantity"]-pos["sell_quantity"]).values[-1])
                        trigger = round(float((df["cp"][-1])*0.997),1)
                    if (pos["sell_quantity"]-pos["buy_quantity"]).values[-1] >0:
                        sell_status = True
                        quantity = int((pos["sell_quantity"]-pos["buy_quantity"]).values[-1])
                        trigger = round(float((df["cp"][-1])*1.003),1)
            if df["signal"][-1] == -1 and not sell_status:
                trigger = round(float((df["close"][-1])*1.003),1)
                placeOrder(ticker, 'NSE_EQ', TransactionType.Sell, quantity)
                slmOrder(ticker, 'NSE_EQ', TransactionType.Buy, quantity, trigger)
            elif df["signal"][-1] == -1 and sell_status:
                modifyOrder(order_id, trigger)
            elif df["signal"][-1] == 1 and not buy_status:
                trigger = round(float((df["close"][-1])*0.997),1)
                placeOrder(ticker, 'NSE_EQ', TransactionType.Buy, quantity)
                slmOrder(ticker, 'NSE_EQ', TransactionType.Sell, quantity, trigger) 
            elif df["signal"][-1] == 1 and buy_status:
                modifyOrder(order_id, trigger)                
            elif df["signal"][-1] == 0 and sell_status:
                try:
                    placeOrder(ticker, 'NSE_EQ', TransactionType.Buy, quantity)
                    try:
                        upstoxAPI.cancel_order(order_id)
                    except:
                        print("can't cancel order")
                except:
                    print("no sell_quantity") 
            elif df["signal"][-1] == 0 and buy_status:
                try:
                    placeOrder(ticker, 'NSE_EQ', TransactionType.Sell, quantity)
                    try:
                        upstoxAPI.cancel_order(order_id)
                    except:
                        print("can't cancel order")
                except:
                    print("no buy_quantity") 
        except:
            print("issue with getting historic data or get instrument call for ",ticker)

starttime=time.time()
timeout = time.time() + 60*345  # 60 seconds times 360 meaning 6 hrs
while time.time() <= timeout:
    try:
        time.sleep(5)
        main()
        time.sleep(300 - ((time.time() - starttime) % 300.0))
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        exit()