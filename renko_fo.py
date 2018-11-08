from upstox_api.api import Upstox, OHLCInterval, TransactionType, OrderType, ProductType, DurationType
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
exclude = ['HINDPETRO'] #excluded tickers

# Get the tickers from Non NIFTY FnO pre market movers
url = 'https://www.nseindia.com/live_market/dynaContent/live_analysis/pre_open/fo.json' #fo.json for non nifty stocks as well
nse = requests.get(url).text
nse = json.loads(nse)['data']
df = pd.DataFrame(nse)
scrips_fo = []
pre_open_fo = df.copy().loc[:,['symbol','perChn','iVal','iep']] #removed mktCap due to data integrity issue and not using it anyways
pre_open_fo.set_index('symbol', drop=True, inplace=True)
pre_open_fo.drop(exclude,inplace=True)
toFloat = lambda x: float(x.replace(",","")) if "," in x else float(x)
pre_open_fo = pre_open_fo.applymap(toFloat)
pre_open_fo = pre_open_fo[pre_open_fo['iep']<0.95*capital]
pre_open_fo = pre_open_fo['perChn'].abs().sort_values(ascending=False)
max_chng_ticker = pre_open_fo.index.values[0]
pre_open_fo = pre_open_fo[pre_open_fo>=3]
if len(pre_open_fo>0):
    n = min(6,len(pre_open_fo))
    scrips_fo = pre_open_fo.index.values.tolist()[:n]
else:
    scrips_fo = [max_chng_ticker]

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
	return upstoxAPI.get_ohlc(scrip,OHLCInterval.Minute_5,dt.date.today()-dt.timedelta(5), dt.date.today())

def renko_bricks(DF):
    "function to calculate trends based on Renko bricks"
    global capital
    renko_df = DF.copy()
    renko_df.columns = ["close","cp","high","low","open","date","volume"]
    renko_df = renko_df.iloc[:,[0,2,3,4,5]]
    renko = Renko(renko_df)
    num = int(capital/renko_df["close"].values[-1])
    renko.brick_size = round((10/num),2)
    df = renko.get_bricks()
    return df

def main_fo():
    global db, capital, scrips_fo
    attempt = 0
    tr = 0
    while attempt<10:
        try:
            pos_df = pd.DataFrame(upstoxAPI.get_positions())
            break
        except:
            print("can't get position information...attempt =",attempt)
            attempt+=1
    iter_fo = scrips_fo.copy()
    print("tickers remaining..",iter_fo)
    for ticker in iter_fo:
        print("starting passthrough for.....",ticker)
        buy_status = False
        sell_status = False
        scrip = upstoxAPI.get_instrument_by_symbol('NSE_EQ', ticker)
        while tr<10:
            try:
                message = fetchOHLC(scrip)
                break
            except:
                print("uanble to fetch hisorical data for ticker ",ticker)
                tr+=1
        df = pd.DataFrame(message)
        df["timestamp"] = pd.to_datetime(df["timestamp"]/1000,unit='s')+ pd.Timedelta('05:30:00')
        renko_df = renko_bricks(df)
        quantity = int(capital/df["close"].values[-1])
        if len(pos_df)>0:
            temp = pos_df[pos_df["symbol"]==ticker]
            pos = temp.copy()
            if len(pos)>0: 
                if (pos["buy_quantity"]-pos["sell_quantity"]).values[-1] >0:
                    buy_status = True
                    quantity = int((pos["buy_quantity"]-pos["sell_quantity"]).values[-1])
                    if pos['realized_profit'].reset_index().iloc[0,-1] == '':
                        pos['realized_profit'] = 0
                    if pos['unrealized_profit'].reset_index().iloc[0,-1] == '':
                        pos['unrealized_profit'] = 0
                    if (pos['realized_profit'].values[0] + pos['unrealized_profit'].values[0]) < -100 or (pos['realized_profit'].values[0] + pos['unrealized_profit'].values[0]) > 200:
                        placeOrder(ticker, 'NSE_EQ', TransactionType.Sell, quantity)
                        print("removing ticker..",ticker)
                        print("realized profit = ",pos['realized_profit'].values[0])
                        print("unrealized profit = ",pos['unrealized_profit'].values[0])
                        scrips_fo.remove(ticker)
                        continue
                if (pos["sell_quantity"]-pos["buy_quantity"]).values[-1] >0:
                    sell_status = True   
                    quantity = int((pos["sell_quantity"]-pos["buy_quantity"]).values[-1])
                    if pos['realized_profit'].reset_index().iloc[0,-1] == '':
                        pos['realized_profit'] = 0
                    if pos['unrealized_profit'].reset_index().iloc[0,-1] == '':
                        pos['unrealized_profit'] = 0
                    if (pos['realized_profit'].values[0] + pos['unrealized_profit'].values[0]) < -100 or (pos['realized_profit'].values[0] + pos['unrealized_profit'].values[0]) > 200:
                        placeOrder(ticker, 'NSE_EQ', TransactionType.Buy, quantity)
                        print("removing ticker..",ticker)
                        print("realized profit = ",pos['realized_profit'].values[0])
                        print("unrealized profit = ",pos['unrealized_profit'].values[0])
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
        print("ending passthrough for.....",ticker)
        
starttime=time.time()
timeout = time.time() + 60*345  # 60 seconds times 360 meaning 6 hrs
while time.time() <= timeout:
    try:
        time.sleep(3)
        main_fo()
        time.sleep(300 - ((time.time() - starttime) % 300.0))
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        exit()