from upstox_api.api import Upstox, TransactionType, OrderType, ProductType, DurationType, LiveFeedType
import time
import os
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
upstoxAPI.get_master_contract('MCX_FO')

shut_down_switch = False #switch to terminate the program

# Scrip details
fut_exchange = "MCX_FO"
fut_contract = "CRUDEOILM18NOVFUT"
ltp_df = [] #initialize list which will store series of ltp
renko_bars = [0,0]


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
    

def renko_live(ltp_list):
    if len(ltp_list)<20:
        return 0
    else:
        brick = 0.1
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
    

def main():
    global shut_down_switch, fut_exchange, fut_contract, ltp_df, renko_bars
    attempt = 0
    tr = 0
    buy_status = False
    sell_status = False
    scrip = upstoxAPI.get_instrument_by_symbol(fut_exchange, fut_contract)
    while attempt<10:
        try:
            pos_df = pd.DataFrame(upstoxAPI.get_positions())
            break
        except:
            print("can't get position information...attempt =",attempt)
            attempt+=1
    while tr<10:
        try:
            message = upstoxAPI.get_live_feed(scrip,LiveFeedType.LTP)
            break
        except:
            print("uanble to fetch ltp data")
            tr+=1
    quantity = 10
    ltp_df.append(message['ltp'])
    if len(ltp_df)>20:
        del ltp_df[0]
    if renko_live(ltp_df) !=0:
        renko_bars.append(renko_live(ltp_df)[-1])
        print(renko_bars)
    if len(pos_df)>0:
        temp = pos_df[pos_df["symbol"]==fut_contract]
        pos = temp.copy()
        if len(pos)>0: 
            if (pos["buy_quantity"]-pos["sell_quantity"]).values[-1] >0:
                buy_status = True
                if pos['realized_profit'].reset_index().iloc[0,-1] == '':
                    pos['realized_profit'] = 0
                if pos['unrealized_profit'].reset_index().iloc[0,-1] == '':
                    pos['unrealized_profit'] = 0
                if (pos['realized_profit'].values[0] + pos['unrealized_profit'].values[0]) < -600 or (pos['realized_profit'].values[0] + pos['unrealized_profit'].values[0]) > 1500:
                    placeOrder(fut_contract, fut_exchange, TransactionType.Sell, quantity)
                    print("circuit hit...shutting down")
                    shut_down_switch = True
            if (pos["sell_quantity"]-pos["buy_quantity"]).values[-1] >0:
                sell_status = True   
                if pos['realized_profit'].reset_index().iloc[0,-1] == '':
                    pos['realized_profit'] = 0
                if pos['unrealized_profit'].reset_index().iloc[0,-1] == '':
                    pos['unrealized_profit'] = 0
                if (pos['realized_profit'].values[0] + pos['unrealized_profit'].values[0]) < -600 or (pos['realized_profit'].values[0] + pos['unrealized_profit'].values[0]) > 1500:
                    placeOrder(fut_contract, fut_exchange, TransactionType.Buy, quantity)
                    print("circuit hit...shutting down")
                    shut_down_switch = True
    if not buy_status and not sell_status:
        if renko_bars[-1]>=2 or (renko_bars[-1]>0 and renko_bars[-2]==1):
            placeOrder(fut_contract, fut_exchange, TransactionType.Buy, quantity)
            print("new long position")
        elif renko_bars[-1]<=-2 or (renko_bars[-1]<0 and renko_bars[-2]==-1):
            placeOrder(fut_contract, fut_exchange, TransactionType.Sell, quantity)
            print("new short position")
    if buy_status:
        if renko_bars[-1]<=-2:
            placeOrder(fut_contract, fut_exchange, TransactionType.Sell, 2*quantity)
            print("changing long position to short position")
        elif renko_bars[-1]==-1:
            placeOrder(fut_contract, fut_exchange, TransactionType.Sell, quantity)
            print("closing out long position")
    if sell_status:
        if renko_bars[-1]>=2:
            placeOrder(fut_contract, fut_exchange, TransactionType.Buy, 2*quantity)
            print("changing short position to long position")
        elif renko_bars[-1]==1:
            placeOrder(fut_contract, fut_exchange, TransactionType.Buy, quantity)
            print("closing out short position")

starttime=time.time()
timeout = time.time() + 60*60  # 60 seconds times 360 meaning 6 hrs
while time.time() <= timeout and not shut_down_switch:
    try:
        main()
        time.sleep(1 - ((time.time() - starttime) % 1.0))
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        exit()
