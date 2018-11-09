from upstox_api.api import Upstox, TransactionType, OrderType, ProductType, DurationType, LiveFeedType
import time
import os
import pandas as pd
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
ltp_df = {} #initialize dictionary which will store series of ltp of each ticker
renko_bars_df = {}

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
pre_open_fo = pre_open_fo[pre_open_fo>=2]
if len(pre_open_fo>0):
    n = min(6,len(pre_open_fo))
    scrips_fo = pre_open_fo.index.values.tolist()[:n]
else:
    scrips_fo = [max_chng_ticker]

for s in scrips_fo:
    renko_bars_df[s] = [0,0]

def placeOrder(symbol, exchange, side, quantity):
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

def renko_live(ltp_list):
    if len(ltp_list)<20:
        return 0
    else:
        num = int(capital/ltp_list[-1])
        brick = round((12/num),2)
        base_up = [ltp_list[0]]
        base_dn = [ltp_list[0] - brick]
        bars = []
        for i in range(1,len(ltp_list)):
            delta = ltp_list[i] - ltp_list[i-1]
            if delta >= 0:
                diff = ltp_list[i] - base_up[-1]
                bars.append(int(diff/brick))
                base_up.append(base_up[-1] + bars[-1]*brick)
                base_dn.append(base_up[-1] - brick)
            if delta < 0:
                diff = ltp_list[i] - base_dn[-1]
                bars.append(int(diff/brick))
                base_up.append(base_up[-1] + bars[-1]*brick)
                base_dn.append(base_up[-1] - brick)
        return bars[-1]
    
def main_fo():
    global capital, scrips_fo, renko_bars_df, ltp_df
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
                message = upstoxAPI.get_live_feed(scrip,LiveFeedType.LTP)
                break
            except:
                print("uanble to fetch hisorical data for ticker ",ticker)
                tr+=1
        if ticker in ltp_df.keys():
            ltp_df[ticker].append(message['ltp'])
        else:
            ltp_df[ticker] = [message['ltp']]
        quantity = int(capital/ltp_df[ticker][-1])
        if len(ltp_df[ticker])>20:
            del ltp_df[ticker][0]
        if renko_live(ltp_df[ticker]) !=0:
            renko_bars_df[ticker].append(renko_live(ltp_df[ticker]))
        print(renko_bars_df[ticker])
        print(ltp_df[ticker])
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
            if renko_bars_df[ticker][-1]>=2 or (renko_bars_df[ticker][-1]>0 and renko_bars_df[ticker][-2]==1):
                placeOrder(ticker, 'NSE_EQ', TransactionType.Buy, quantity)
                print("new long position")
            elif renko_bars_df[ticker][-1]<=-2 or (renko_bars_df[ticker][-1]<0 and renko_bars_df[ticker][-2]==-1):
                placeOrder(ticker, 'NSE_EQ', TransactionType.Sell, quantity)
                print("new short position")
        if buy_status:
            if renko_bars_df[ticker][-1]<=-2:
                placeOrder(ticker, 'NSE_EQ', TransactionType.Sell, 2*quantity)
                print("changing long position to short position")
            elif renko_bars_df[ticker][-1]==-1:
                placeOrder(ticker, 'NSE_EQ', TransactionType.Sell, quantity)
                print("closing out long position")
        if sell_status:
            if renko_bars_df[ticker][-1]>=2:
                placeOrder(ticker, 'NSE_EQ', TransactionType.Buy, 2*quantity)
                print("changing short position to long position")
            elif renko_bars_df[ticker][-1]==1:
                placeOrder(ticker, 'NSE_EQ', TransactionType.Buy, quantity)
                print("closing out short position")
        
starttime=time.time()
timeout = time.time() + 60*30  # 60 seconds times 360 meaning 6 hrs
while time.time() <= timeout:
    try:
        main_fo()
        #time.sleep(300 - ((time.time() - starttime) % 300.0))
        time.sleep(1)
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        exit()