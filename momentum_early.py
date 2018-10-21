from upstox_api.api import Upstox, TransactionType, OrderType, ProductType, DurationType, LiveFeedType
import time
import os
import requests, json
import pandas as pd

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
ltp_df = {} #initialize dictionary which will store series of ltp of each ticker

# Get the tickers from Non NIFTY FnO pre market movers
url = 'https://www.nseindia.com/live_market/dynaContent/live_analysis/pre_open/fo.json' #fo.json for non nifty stocks as well
nse = requests.get(url).text
nse = json.loads(nse)['data']
df = pd.DataFrame(nse)
scrips_fo = []
pre_open_fo = df.copy().loc[:,['mktCap','symbol','perChn','iVal','iep']]
pre_open_fo.set_index('symbol', drop=True, inplace=True)
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
        if len(scrips_fo) ==6:
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
    
def signal(ser):
    arr_int = ser
    if arr_int[-1]/arr_int[0] >=1.003 or arr_int[-1]>arr_int[-2]>arr_int[-3]:
        signal = "buy"
    if arr_int[-1]/arr_int[0] <=0.997 or arr_int[-1]<arr_int[-2]<arr_int[-3]:
        signal = "sell"
    else:
        signal = "hold"
    return signal  
    

def main():
    global ltp_df, scrips
    attempt = 0
    while attempt<10:
        try:
            pos_df = pd.DataFrame(upstoxAPI.get_positions())
            break
        except:
            print("can't get position information...attempt =",attempt)
            attempt+=1
    for ticker in scrips_fo:
        buy_status = False
        sell_status = False
        scrip = upstoxAPI.get_instrument_by_symbol('NSE_EQ', ticker)
        message = upstoxAPI.get_live_feed(scrip,LiveFeedType.LTP)
        quantity = int(capital/message['ltp'])
        if len(pos_df)>0:
            pos = pos_df[pos_df["symbol"]==ticker]
            if len(pos)>0: 
                if (pos["buy_quantity"]-pos["sell_quantity"]).values[-1] >0:
                    buy_status = True
                    quantity = int((pos["buy_quantity"]-pos["sell_quantity"]).values[-1])
                if (pos["sell_quantity"]-pos["buy_quantity"]).values[-1] >0:
                    sell_status = True   
                    quantity = int((pos["sell_quantity"]-pos["buy_quantity"]).values[-1])
        if ticker in ltp_df.keys():
            ltp_df[ticker].append(message['ltp'])
        else:
            ltp_df[ticker] = [message['ltp']]
        if len(ltp_df[ticker]) >= 5:
            del ltp_df[ticker][0]
            if signal(ltp_df[ticker]) == 'buy':
                if sell_status:
                    placeOrder(ticker, 'NSE_EQ', TransactionType.Buy, 2*quantity)
                if not sell_status and not buy_status:
                    placeOrder(ticker, 'NSE_EQ', TransactionType.Buy, quantity)
            if signal(ltp_df[ticker]) == 'sell':
                if buy_status:
                    placeOrder(ticker, 'NSE_EQ', TransactionType.Sell, 2*quantity)
                if not sell_status and not buy_status:
                    placeOrder(ticker, 'NSE_EQ', TransactionType.Sell, quantity)
        

timeout = time.time() + 60*15  # 10 seconds times 1
while time.time() <= timeout:
    try:
        main()
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        exit()
