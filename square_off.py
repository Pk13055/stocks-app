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
time.sleep(1)
upstoxAPI.get_master_contract('MCX_FO')
time.sleep(1)

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

#time.sleep(10)

attempt = 0
while attempt<10:
    try:
        pos_df = pd.DataFrame(upstoxAPI.get_positions())
        break
    except:
        print("can't get position...attempt =",attempt)
        attempt+=1

time.sleep(1)      
for i in range(len(pos_df)):
    ticker = pos_df["symbol"].values[i]
    if (pos_df["buy_quantity"]-pos_df["sell_quantity"]).values[i] >0:
        quantity = int((pos_df["buy_quantity"]-pos_df["sell_quantity"]).values[i])
        if pos_df["exchange"].values[i] == "NSE_EQ":
            placeOrder(ticker, 'NSE_EQ', TransactionType.Sell, quantity)
            time.sleep(1)
        elif pos_df["exchange"].values[i] == "MCX_FO":
            quantity = 10
            placeOrder(ticker, 'MCX_FO', TransactionType.Sell, quantity)
            time.sleep(1)
    if (pos_df["sell_quantity"]-pos_df["buy_quantity"]).values[i] >0:
        quantity = int((pos_df["sell_quantity"]-pos_df["buy_quantity"]).values[i])
        if pos_df["exchange"].values[i] == "NSE_EQ":
            placeOrder(ticker, 'NSE_EQ', TransactionType.Buy, quantity)
            time.sleep(1)
        elif pos_df["exchange"].values[i] == "MCX_FO":
            quantity = 10
            placeOrder(ticker, 'MCX_FO', TransactionType.Buy, quantity)
            time.sleep(1)