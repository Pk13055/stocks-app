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

capital = 5000 #max capital allocated to each stock

# Get the tickers from NIFTY pre market movers
url = 'https://www.nseindia.com/live_market/dynaContent/live_analysis/pre_open/nifty.json' #fo.json for non nifty stocks as well
nse = requests.get(url).text
nse = json.loads(nse)['data']
df = pd.DataFrame(nse)
pre_open_nfty = df.copy().loc[:,['symbol','perChn','iVal','iep']]
pre_open_nfty.set_index('symbol', drop=True, inplace=True)
toFloat = lambda x: float(x.replace(",","")) if "," in x else float(x)
pre_open_nfty = pre_open_nfty.applymap(toFloat)
pre_open_nfty = pre_open_nfty[pre_open_nfty['iep']<0.95*capital]
#pre_open_nfty['weight'] = (0.6*10)*abs(pre_open_nfty['perChn']) + (0.3/70)*pre_open_nfty['iVal'] + (0.1/60000)*pre_open_nfty['mktCap']
pre_open_nfty.sort_values(by=['iVal'],ascending=False,inplace=True)
scrips_nfty = pre_open_nfty.iloc[:5,:].index.values.tolist() # change the number after iloc to get required numbers of tickers

# Get the tickers from Non NIFTY FnO pre market movers
url = 'https://www.nseindia.com/live_market/dynaContent/live_analysis/pre_open/fo.json' #fo.json for non nifty stocks as well
nse = requests.get(url).text
nse = json.loads(nse)['data']
df = pd.DataFrame(nse)
scrips_fo = []
pre_open_fo = df.copy().loc[:,['mktCap','symbol','perChn','iVal','iep']]
pre_open_fo.set_index('symbol', drop=True, inplace=True)
pre_open_fo.drop(pre_open_nfty.index,inplace=True)
toFloat = lambda x: float(x.replace(",","")) if "," in x else float(x)
scrips_fo = pre_open_fo['perChn'].apply(toFloat).abs().sort_values(ascending=False).index.values.tolist()[:3]
pre_open_fo = pre_open_fo[pre_open_fo['mktCap']!='-']
pre_open_fo = pre_open_fo.applymap(toFloat)
pre_open_fo['ratio'] = pre_open_fo['iVal']/pre_open_fo['mktCap']
pre_open_fo = pre_open_fo[pre_open_fo['iep']<0.95*capital]
pre_open_fo.sort_values(by=['ratio'],ascending=False,inplace=True)
for t in pre_open_fo.index.values.tolist():
    if t not in scrips_fo:
        scrips_fo.append(t)
        if len(scrips_fo) ==5:
            break

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
    if renko_df["close"].values[-1] >= 90:
        renko.brick_size = max(1,int(renko_df['close'].max()*0.003))
    elif 30 <= renko_df["close"].values[-1] < 90:
        renko.brick_size = 0.5
    else:
        renko.brick_size = 0.2
    df = renko.get_bricks()
    return df

def main_nfty():
    global db, capital, scrips_nfty
    attempt = 0
    while attempt<10:
        try:
            pos_df = pd.DataFrame(upstoxAPI.get_positions())
            if len(pos_df)>0:
                break
        except:
            print("can't get position information...attempt =",attempt)
            attempt+=1
    iter_nifty = scrips_nfty.copy()
    for ticker in iter_nifty:
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
                        if pos['realized_profit'].reset_index().iloc[0,-1] == '':
                            pos['realized_profit'] == 0
                        if pos['unrealized_profit'].reset_index().iloc[0,-1] == '':
                            pos['unrealized_profit'] == 0
                        if abs(pos['realized_profit'].values[0] + pos['unrealized_profit'].values[0]) >= 100:
                            placeOrder(ticker, 'NSE_EQ', TransactionType.Sell, quantity)
                            scrips_nfty.remove(ticker)
                            continue
                    if (pos["sell_quantity"]-pos["buy_quantity"]).values[-1] >0:
                        sell_status = True   
                        quantity = int((pos["sell_quantity"]-pos["buy_quantity"]).values[-1])
                        if pos['realized_profit'].reset_index().iloc[0,-1] == '':
                            pos['realized_profit'] == 0
                        if pos['unrealized_profit'].reset_index().iloc[0,-1] == '':
                            pos['unrealized_profit'] == 0
                        if abs(pos['realized_profit'].values[0] + pos['unrealized_profit'].values[0]) >= 100:
                            placeOrder(ticker, 'NSE_EQ', TransactionType.Buy, quantity)
                            scrips_nfty.remove(ticker)
                            continue
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

def main_fo():
    global db, capital, scrips_fo
    attempt = 0
    while attempt<10:
        try:
            pos_df = pd.DataFrame(upstoxAPI.get_positions())
            if len(pos_df)>0:
                break
        except:
            print("can't get position information...attempt =",attempt)
            attempt+=1
    iter_fo = scrips_fo.copy()
    for ticker in iter_fo:
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
                        if abs(pos['realized_profit'].values[0] + pos['unrealized_profit'].values[0]) >= 100:
                            placeOrder(ticker, 'NSE_EQ', TransactionType.Sell, quantity)
                            scrips_fo.remove(ticker)
                            continue
                    if (pos["sell_quantity"]-pos["buy_quantity"]).values[-1] >0:
                        sell_status = True   
                        quantity = int((pos["sell_quantity"]-pos["buy_quantity"]).values[-1])
                        if abs(pos['realized_profit'].values[0] + pos['unrealized_profit'].values[0]) >= 100:
                            placeOrder(ticker, 'NSE_EQ', TransactionType.Buy, quantity)
                            scrips_fo.remove(ticker)
                            continue
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
timeout = time.time() + 60*340  # 60 seconds times 360 meaning 6 hrs
while time.time() <= timeout:
    try:
        time.sleep(5)
        main_nfty()
        main_fo()
        time.sleep(300 - ((time.time() - starttime) % 300.0))
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        exit()