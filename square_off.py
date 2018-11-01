from upstox_api.api import Upstox, TransactionType, OrderType, ProductType, DurationType
import os
import pandas as pd
import time

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
upstoxAPI.get_master_contract('MCX_FO')

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

time.sleep(60)

attempt = 0
while attempt<10:
    try:
        pos_df = pd.DataFrame(upstoxAPI.get_positions())
        break
    except:
        print("can't get position...attempt =",attempt)
        attempt+=1
        
for i in range(len(pos_df)):
    ticker = pos_df["symbol"].values[i]
    if (pos_df["buy_quantity"]-pos_df["sell_quantity"]).values[i] >0:
        quantity = int((pos_df["buy_quantity"]-pos_df["sell_quantity"]).values[i])
        placeOrder(ticker, 'NSE_EQ', TransactionType.Sell, quantity)
    if (pos_df["sell_quantity"]-pos_df["buy_quantity"]).values[i] >0:
        quantity = int((pos_df["sell_quantity"]-pos_df["buy_quantity"]).values[i])
        placeOrder(ticker, 'NSE_EQ', TransactionType.Buy, quantity)