from upstox_api.api import Upstox, OHLCInterval, TransactionType, OrderType, ProductType, DurationType
import time
import os
import pandas as pd
import datetime as dt
from stocktrends import Renko

cwd = os.getcwd()

access_token = open(os.path.join(cwd,"access_token.txt"),'r').read()

config = {
	'apiKey': 'AAJ0Rx0qDu5TExtIOhEIH1od78siET7t6SuMiGsO',
	'accessToken': access_token
}

# Create the UpstoxAPI object bound to your API key
upstoxAPI = Upstox(config['apiKey'], config['accessToken'])

# get master contract for MCX EQ
upstoxAPI.get_master_contract('MCX_FO')

shut_down_switch = False #switch to terminate the program

# Scrip details
fut_exchange = "MCX_FO"
fut_contract = "CRUDEOILM18NOVFUT"
#SCRIP = upstoxAPI.get_instrument_by_symbol(fut_exchange, fut_contract)



def placeOrder(contract, exchange, side, quantity):
    SCRIP = upstoxAPI.get_instrument_by_symbol(exchange, contract)
    upstoxAPI.place_order(
		side,  # transaction_type
		SCRIP,  # instrument
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
	return upstoxAPI.get_ohlc(scrip,OHLCInterval.Minute_1,dt.date.today()-dt.timedelta(5), dt.date.today())

def renko_bricks(DF):
    "function to calculate trends based on Renko bricks"
    renko_df = DF.copy()
    renko_df.columns = ["close","cp","high","low","open","date","volume"]
    renko_df = renko_df.iloc[:,[0,2,3,4,5]]
    renko = Renko(renko_df)
    renko.brick_size = 7
    df = renko.get_bricks()
    return df

def main_fo():
    global shut_down_switch, fut_exchange, fut_contract
    attempt = 0
    while attempt<10:
        try:
            pos_df = pd.DataFrame(upstoxAPI.get_positions())
            break
        except:
            print("can't get position information...attempt =",attempt)
            attempt+=1
    buy_status = False
    sell_status = False
    scrip = upstoxAPI.get_instrument_by_symbol(fut_exchange, fut_contract)
    message = fetchOHLC(scrip)
    df = pd.DataFrame(message)
    df["timestamp"] = pd.to_datetime(df["timestamp"]/1000,unit='s')+ pd.Timedelta('05:30:00')
    renko_df = renko_bricks(df)
    quantity = 10
    if len(pos_df)>0:
        pos = pos_df[pos_df["symbol"]==fut_contract]
        if len(pos)>0: 
            if (pos["buy_quantity"]-pos["sell_quantity"]).values[-1] >0:
                buy_status = True
                if pos['realized_profit'].reset_index().iloc[0,-1] == '':
                    pos['realized_profit'] = 0
                if pos['unrealized_profit'].reset_index().iloc[0,-1] == '':
                    pos['unrealized_profit'] = 0
                if (pos['realized_profit'].values[0] + pos['unrealized_profit'].values[0]) < -600 or (pos['realized_profit'].values[0] + pos['unrealized_profit'].values[0]) > 1500:
                    placeOrder(fut_contract, fut_exchange, TransactionType.Sell, quantity)
                    shut_down_switch = True
            if (pos["sell_quantity"]-pos["buy_quantity"]).values[-1] >0:
                sell_status = True   
                if pos['realized_profit'].reset_index().iloc[0,-1] == '':
                    pos['realized_profit'] = 0
                if pos['unrealized_profit'].reset_index().iloc[0,-1] == '':
                    pos['unrealized_profit'] = 0
                if (pos['realized_profit'].values[0] + pos['unrealized_profit'].values[0]) < -600 or (pos['realized_profit'].values[0] + pos['unrealized_profit'].values[0]) > 1500:
                    placeOrder(fut_contract, fut_exchange, TransactionType.Buy, quantity)
                    shut_down_switch = True
    if not buy_status and not sell_status:
        if renko_df["uptrend"].values[-1] and renko_df["uptrend"].values[-2]:
            placeOrder(fut_contract, fut_exchange, TransactionType.Buy, quantity)
        elif not renko_df["uptrend"].values[-1] and not renko_df["uptrend"].values[-2]:
            placeOrder(fut_contract, fut_exchange, TransactionType.Sell, quantity)
    if buy_status:
        if not renko_df["uptrend"].values[-1] and not renko_df["uptrend"].values[-2]:
            placeOrder(fut_contract, fut_exchange, TransactionType.Sell, 2*quantity)
        elif not renko_df["uptrend"].values[-1] or not renko_df["uptrend"].values[-2]:
            placeOrder(fut_contract, fut_exchange, TransactionType.Sell, quantity)
    if sell_status:
        if renko_df["uptrend"].values[-1] and renko_df["uptrend"].values[-2]:
            placeOrder(fut_contract, fut_exchange, TransactionType.Buy, 2*quantity)
        elif renko_df["uptrend"].values[-1] or renko_df["uptrend"].values[-2]:
            placeOrder(fut_contract, fut_exchange, TransactionType.Buy, quantity)


starttime=time.time()
timeout = time.time() + 60*690  # 60 seconds times 360 meaning 6 hrs
while time.time() <= timeout and not shut_down_switch:
    try:
        time.sleep(2)
        main_fo()
        time.sleep(60 - ((time.time() - starttime) % 60.0))
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        exit()