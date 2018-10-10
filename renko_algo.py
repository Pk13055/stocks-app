from upstox_api.api import Upstox, datetime, OHLCInterval, TransactionType, OrderType, ProductType, DurationType
import time
import os
import pandas as pd
import datetime as dt
from stocktrends import Renko
import requests, json

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

# Get the tickers from NSE pre market movers
url = 'https://www.nseindia.com/live_market/dynaContent/live_analysis/pre_open/nifty.json' #fo.json for non nifty stocks as well
nse = requests.get(url).text
nse = json.loads(nse)['data']
df = pd.DataFrame(nse)
pre_open = df.copy().loc[:,['mktCap','symbol','perChn','iVal']]
pre_open.set_index('symbol', drop=True, inplace=True)
toFloat = lambda x: float(x.replace(",","")) if "," in x else float(x)
pre_open = pre_open.applymap(toFloat)
pre_open['weight'] = (0.6*10)*abs(pre_open['perChn']) + (0.3/70)*pre_open['iVal'] + (0.1/60000)*pre_open['mktCap']
pre_open.sort_values(by=['weight'],ascending=False,inplace=True)
scrips = pre_open.iloc[:5,:].index.values.tolist() # change the number after iloc to get required numbers of tickers

capital = 5000 #max capital allocated to each stock

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

def fetchOHLC(scrip):
	return upstoxAPI.get_ohlc(scrip,OHLCInterval.Minute_5,dt.date.today()-dt.timedelta(15), dt.date.today())

def renko_bricks(DF):
    "function to calculate trends based on Renko bricks"
    renko_df = DF.copy()
    renko_df.columns = ["close","cp","high","low","open","date","volume"]
    renko_df = renko_df.iloc[:,[0,2,3,4,5]]
    renko = Renko(renko_df)
    renko.brick_size = max(1,int(renko_df['close'].max()*0.003))
    df = renko.get_bricks()
    return df

def main():
    global db, capital
    attempt = 0
    while attempt<10:
        try:
            pos_df = pd.DataFrame(upstoxAPI.get_positions())
            break
        except:
            print("can't get position information...attempt =",attempt)
            attempt+=1
    for ticker in scrips:
        buy_status = False
        sell_status = False
        try:
            scrip = upstoxAPI.get_instrument_by_symbol('NSE_EQ', ticker)
            message = fetchOHLC(scrip)
            df = pd.DataFrame(message)
            df["timestamp"] = pd.to_datetime(df["timestamp"]/1000,unit='s')+ pd.Timedelta('05:30:00')
            renko_df = renko_bricks(df)
            quantity = int(capital/df["close"].values[-1])
            if len(pos_df)>0:
                pos = pos_df[pos_df["symbol"]==ticker]
                if len(pos)>0: 
                    if (pos["buy_quantity"]-pos["sell_quantity"]).values[-1] >0:
                        buy_status = True
                        quantity = int((pos["buy_quantity"]-pos["sell_quantity"]).values[-1])
                    if (pos["sell_quantity"]-pos["buy_quantity"]).values[-1] >0:
                        sell_status = True   
                        quantity = int((pos["sell_quantity"]-pos["buy_quantity"]).values[-1])
            if not buy_status and not sell_status:
                if renko_df["uptrend"].values[-1] and renko_df["uptrend"].values[-2]:
                    placeOrder(ticker, 'NSE_EQ', TransactionType.Buy, quantity)
                elif not renko_df["uptrend"].values[-1] and not renko_df["uptrend"].values[-2]:
                    placeOrder(ticker, 'NSE_EQ', TransactionType.Sell, quantity)
            if buy_status:
                if not renko_df["uptrend"].values[-1] and not renko_df["uptrend"].values[-2]:
                    placeOrder(ticker, 'NSE_EQ', TransactionType.Sell, 2*quantity)
                elif not renko_df["uptrend"].values[-1] or not renko_df["uptrend"].values[-2]:
                    placeOrder(ticker, 'NSE_EQ', TransactionType.Sell, quantity)
            if sell_status:
                if renko_df["uptrend"].values[-1] and renko_df["uptrend"].values[-2]:
                    placeOrder(ticker, 'NSE_EQ', TransactionType.Buy, 2*quantity)
                elif renko_df["uptrend"].values[-1] or renko_df["uptrend"].values[-2]:
                    placeOrder(ticker, 'NSE_EQ', TransactionType.Buy, quantity)
        except:
            print("API Issue......")


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