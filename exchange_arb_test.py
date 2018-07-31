from upstox_api.api import Upstox, LiveFeedType
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

def current_quote(message):
    global ask_price_nse, bid_price_nse, ask_price_bse, bid_price_bse
    if message['exchange'] == 'NSE_EQ':
        try:
            ask_price_nse = float(message['asks'][0]['price'])
            bid_price_nse = float(message['bids'][0]['price'])
            print("stock %s: bid price NSE = %.2f, ask price NSE = %.2f"%(message['symbol'],bid_price_nse,ask_price_nse))
        except:
            pass
    elif message['exchange'] == 'BSE_EQ':
        try:
            ask_price_bse = float(message['asks'][0]['price'])
            bid_price_bse = float(message['bids'][0]['price'])
            print("stock %s: bid price BSE = %.2f, ask price BSE = %.2f"%(message['symbol'],bid_price_bse,ask_price_bse))
        except:
            pass
    if ask_price_nse != 0 and bid_price_nse !=0 and ask_price_bse !=0 and bid_price_bse !=0:
        diff1 = (bid_price_nse - ask_price_bse)/ask_price_bse
        diff2 = (bid_price_bse - ask_price_nse)/ask_price_nse
        if diff1 >= 0.02:
            print("stock %s: sell NSE at %.2f ,buy BSE at %.2f"%(message['symbol'],bid_price_nse,ask_price_bse))
        elif diff2 >= 0.02:
            print("stock %s: buy NSE at %.2f ,sell BSE at %.2f"%(message['symbol'],ask_price_nse,bid_price_bse))
    #print("Quote Update: %s" % str(message))

#upstoxAPI.get_balance()["equity"]["available_margin"]

def main():
    for ticker in scrips:
        scrip1 = upstoxAPI.get_instrument_by_symbol('NSE_EQ', ticker)
        message1 = upstoxAPI.get_live_feed(scrip1,LiveFeedType.Full)
        current_quote(message1)
        scrip2 = upstoxAPI.get_instrument_by_symbol('BSE_EQ', ticker)
        message2 = upstoxAPI.get_live_feed(scrip2,LiveFeedType.Full)
        current_quote(message2)
 

timeout = time.time() + 10*1  # 10 seconds times 1
while time.time() <= timeout:
    try:
        main()
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        exit()
