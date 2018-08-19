from upstox_api.api import Upstox, LiveFeedType, OrderType, TransactionType, ProductType, DurationType
import time
import os

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
upstoxAPI.get_master_contract('BSE_EQ')

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

ask_price_nse = 0
bid_price_nse = 0
ask_price_bse = 0
bid_price_bse = 0
ask_supply_nse = 0
bid_supply_nse = 0
ask_supply_bse = 0
bid_supply_bse = 0
symbol_nse = ''
symbol_bse = ''
capital = 30000 # this should be half of total true intraday capital
pflio = {}

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

def current_quote(message):
    global ask_price_nse, bid_price_nse, ask_price_bse, bid_price_bse, symbol_nse, symbol_bse
    global ask_supply_nse, bid_supply_nse, ask_supply_bse, bid_supply_bse, capital, pflio
    if message['exchange'] == 'NSE_EQ':
        try:
            ask_price_nse = float(message['asks'][0]['price'])
            ask_supply_nse = int(message['asks'][0]['quantity'])
            bid_price_nse = float(message['bids'][0]['price'])
            bid_supply_nse = int(message['bids'][0]['quantity'])
            symbol_nse = message['symbol']
            #print("stock %s: bid price NSE = %.2f, ask price NSE = %.2f"%(message['symbol'],bid_price_nse,ask_price_nse))
        except:
            pass
    elif message['exchange'] == 'BSE_EQ':
        try:
            ask_price_bse = float(message['asks'][0]['price'])
            ask_supply_bse = int(message['asks'][0]['quantity'])
            bid_price_bse = float(message['bids'][0]['price'])
            bid_supply_bse = int(message['bids'][0]['quantity'])
            symbol_bse = message['symbol']
            #print("stock %s: bid price BSE = %.2f, ask price BSE = %.2f"%(message['symbol'],bid_price_bse,ask_price_bse))
        except:
            pass
    if ask_price_nse != 0 and bid_price_nse !=0 and ask_price_bse !=0 and bid_price_bse !=0 and symbol_nse==symbol_bse:
        diff1 = (bid_price_nse - ask_price_bse)/ask_price_bse
        diff2 = (bid_price_bse - ask_price_nse)/ask_price_nse
        if diff1 >= 0.003 and (bid_price_nse - ask_price_bse)*min(bid_supply_nse,ask_supply_bse)>=50 and message['symbol'] not in pflio:
            quantity = min(int(capital/bid_price_nse),min(bid_supply_nse,ask_supply_bse))
            placeOrder(message['symbol'],'NSE_EQ',TransactionType.Sell,quantity)
            placeOrder(message['symbol'],'BSE_EQ',TransactionType.Buy,quantity)
            pflio[message['symbol']] = ['NSE_EQ','BSE_EQ',quantity]
            capital = (2*capital - (bid_price_nse + ask_price_bse)*quantity)/2
            print("stock %s: sold NSE at %.3f and bought BSE at %.3f : supply %d"%(message['symbol'],bid_price_nse,ask_price_bse,quantity))
            print("remaining capital :",capital*2)
            print("portfolio :",pflio)
        elif diff2 >= 0.003 and (bid_price_bse - ask_price_nse)*min(bid_supply_bse,ask_supply_nse)>=50 and message['symbol'] not in pflio:
            quantity = min(int(capital/bid_price_bse),min(bid_supply_bse,ask_supply_nse))
            placeOrder(message['symbol'],'BSE_EQ',TransactionType.Sell,quantity)
            placeOrder(message['symbol'],'NSE_EQ',TransactionType.Buy,quantity)
            pflio[message['symbol']] = ['BSE_EQ','NSE_EQ',quantity]
            capital = (2*capital - (bid_price_bse + ask_price_nse)*quantity)/2
            print("stock %s: bought NSE at %.3f and sold BSE at %.3f : supply %d"%(message['symbol'],ask_price_nse,bid_price_bse,quantity))
            print("remaining capital :",capital*2)
            print("portfolio :",pflio)
        elif diff1 <= 0.0005 and diff2 <= 0.0005 and message['symbol'] in pflio:
            buy_exchange = pflio[message['symbol']][0]
            sell_exchange = pflio[message['symbol']][1]
            q = pflio[message['symbol']][2]
            placeOrder(message['symbol'],buy_exchange,TransactionType.Buy,q)
            placeOrder(message['symbol'],sell_exchange,TransactionType.Sell,q)
            pflio.pop(message['symbol'],None)
            capital = capital + q*min(bid_price_bse,bid_price_nse,ask_price_bse,ask_price_nse)
            print("profit realized for stock %s"%message['symbol'])
            print("remaining capital :",capital*2)
            print("portfolio :",pflio)
            
            
#upstoxAPI.get_balance()["equity"]["available_margin"]

def main():
    for ticker in scrips:
        try:
            scrip1 = upstoxAPI.get_instrument_by_symbol('NSE_EQ', ticker)
            message1 = upstoxAPI.get_live_feed(scrip1,LiveFeedType.Full)
            current_quote(message1)
            scrip2 = upstoxAPI.get_instrument_by_symbol('BSE_EQ', ticker)
            message2 = upstoxAPI.get_live_feed(scrip2,LiveFeedType.Full)
            current_quote(message2)
        except:
            print("issue with get live feed call or get instrument call")

timeout = time.time() + 60*60  # 60 seconds times 360 meaning 6 hrs
while time.time() <= timeout:
    try:
        main()
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        exit()