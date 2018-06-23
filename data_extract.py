"""
Extracting relavent stock and fundamental data for relevant stocks
to be run everyday as 6PM IST

Author   - Mayank Rasu
"""

# importing libraries
import requests
import csv
from bs4 import BeautifulSoup
import os
import pandas as pd
import pandas_datareader.data as pdr
import datetime

cwd = os.getcwd() # getting current working directory to save output files

all_tickers = ["ZEEL.NS","YESBANK.NS","WOCKPHARMA.NS","WIPRO.NS","VOLTAS.NS","VEDL.NS",
               "VAKRANGEE.NS","VGUARD.NS","MCDOWELL-N.NS","UBL.NS","UNIONBANK.NS",
               "ULTRACEMCO.NS","UPL.NS","TORNTPOWER.NS","TORNTPHARM.NS","TITAN.NS",
               "RAMCOCEM.NS","TECHM.NS","TATASTEEL.NS","TATAPOWER.NS","TATAMOTORS.NS",
               "TATAMTRDVR.NS","TATAGLOBAL.NS","TCS.NS","TATACOMM.NS","TATACHEM.NS",
               "TVSMOTOR.NS","TV18BRDCST.NS","SYNGENE.NS","SUZLON.NS","SUNTV.NS",
               "SUNPHARMA.NS","SPARC.NS","STRTECH.NS","SAIL.NS","SBIN.NS","SIEMENS.NS",
               "SRTRANSFIN.NS","SHREECEM.NS","SRF.NS","SBILIFE.NS","RECLTD.NS","RPOWER.NS",
               "RELINFRA.NS","RELIANCE.NS","RELCAPITAL.NS","RAJESHEXPO.NS","RBLBANK.NS",
               "PNB.NS","PGHH.NS","PRESTIGE.NS","POWERGRID.NS","PFC.NS","PEL.NS",
               "PIDILITIND.NS","PETRONET.NS","PAGEIND.NS","PNBHOUSING.NS","PIIND.NS",
               "PCJEWELLER.NS","OFSS.NS","OIL.NS","ONGC.NS","OBEROIRLTY.NS","NATIONALUM.NS",
               "NTPC.NS","NMDC.NS","NHPC.NS","NBCC.NS","NATCOPHARM.NS","MUTHOOTFIN.NS",
               "MPHASIS.NS","MOTHERSUMI.NS","MINDTREE.NS","MFSL.NS","MARUTI.NS","MARICO.NS",
               "MRPL.NS","MANAPPURAM.NS","M&M.NS","M&MFIN.NS","MGL.NS","MRF.NS","LUPIN.NS",
               "LT.NS","LICHSGFIN.NS","L&TFH.NS","KOTAKBANK.NS","KARURVYSYA.NS","JUBILANT.NS",
               "JUBLFOOD.NS","JINDALSTEL.NS","JSWSTEEL.NS","JSWENERGY.NS","INDIGO.NS",
               "INFY.NS","NAUKRI.NS","INDUSINDBK.NS","IGL.NS","IOC.NS","INDHOTEL.NS",
               "INDIANB.NS","IBVENTURES.NS","IBREALEST.NS","IBULHSGFIN.NS","IDEA.NS",
               "IRB.NS","IDFC.NS","IDFCBANK.NS","IDBI.NS","ICICIPRULI.NS","ICICIGI.NS",
               "ICICIBANK.NS","ITC.NS","HDFC.NS","HUDCO.NS","HINDZINC.NS","HINDUNILVR.NS",
               "HINDPETRO.NS","HINDALCO.NS","HEXAWARE.NS","HEROMOTOCO.NS","HAVELLS.NS",
               "HDFCBANK.NS","HCLTECH.NS","GSPL.NS","GRUH.NS","GRASIM.NS","GODREJIND.NS",
               "GODREJCP.NS","GODREJAGRO.NS","GLENMARK.NS","GICRE.NS","GMRINFRA.NS",
               "GAIL.NS","FCONSUMER.NS","FEDERALBNK.NS","EXIDEIND.NS","ENGINERSIN.NS",
               "ENDURANCE.NS","EMAMILTD.NS","EICHERMOT.NS","EDELWEISS.NS","DRREDDY.NS",
               "DIVISLAB.NS","DISHTV.NS","DBL.NS","DHFL.NS","DABUR.NS","DLF.NS","CUMMINSIND.NS",
               "CROMPTON.NS","COROMANDEL.NS","CONCOR.NS","COLPAL.NS","COALINDIA.NS","CIPLA.NS",
               "CHOLAFIN.NS","CENTURYTEX.NS","CENTRALBK.NS","CASTROLIND.NS","CANBK.NS",
               "CADILAHC.NS","BRITANNIA.NS","BOSCHLTD.NS","BIOCON.NS","INFRATEL.NS",
               "BHARTIARTL.NS","BPCL.NS","BHEL.NS","BHARATFORG.NS","BHARATFIN.NS","BEL.NS",
               "BERGEPAINT.NS","BATAINDIA.NS","BANKINDIA.NS","BANKBARODA.NS","BALKRISIND.NS",
               "BAJAJFINSV.NS","BAJFINANCE.NS","BAJAJ-AUTO.NS","AXISBANK.NS","DMART.NS",
               "AUROPHARMA.NS","ASIANPAINT.NS","ASHOKLEY.NS","ARVIND.NS","APOLLOTYRE.NS",
               "APOLLOHOSP.NS","AMBUJACEM.NS","AMARAJABAT.NS","ALKEM.NS","AJANTPHARM.NS",
               "ABFRL.NS","ABCAPITAL.NS","ADANIPOWER.NS","ADANIPORTS.NS","AUBANK.NS",
               "AIAENG.NS","ACC.NS","ABB.NS"]

##########Web scraping to extract relevant fundamental data for companies######
for ticker in all_tickers:
    try:
        url = 'https://in.finance.yahoo.com/quote/'+ticker+'/balance-sheet?p='+ticker
        page = requests.get(url)
        contents = page.content
        soup = BeautifulSoup(contents, 'html.parser')
        tabl = soup.findAll("table", {"class": "Lh(1.7) W(100%) M(0)"})
        for t in tabl:
            rows = t.findAll('tr')
            with open(cwd+'/financials_{}.csv'.format(ticker),'w') as File:
                for row in rows:
                    prnt = row.get_text(separator='|').replace(",","")
                    doc = csv.writer(File)
                    doc.writerow(prnt.split('|'))
                File.close()
        url2 = 'https://in.finance.yahoo.com/quote/'+ticker+'/financials?p='+ticker
        page2 = requests.get(url2)
        contents2 = page2.content
        soup2 = BeautifulSoup(contents2, 'html.parser')
        tabl2 = soup2.findAll("table", {"class": "Lh(1.7) W(100%) M(0)"})
        for t2 in tabl2:
            rows2 = t2.findAll('tr')
            with open(cwd+'/financials_{}.csv'.format(ticker),'a') as File:
                for row in rows2:
                    prnt = row.get_text(separator='|').replace(",","")
                    doc = csv.writer(File)
                    doc.writerow(prnt.split('|'))
                File.close()
        url3 = 'https://in.finance.yahoo.com/quote/'+ticker+'/cash-flow?p='+ticker
        page3 = requests.get(url3)
        contents3 = page3.content
        soup3 = BeautifulSoup(contents3, 'html.parser')
        tabl3 = soup3.findAll("table", {"class": "Lh(1.7) W(100%) M(0)"})
        for t3 in tabl3:
            rows3 = t3.findAll('tr')
            with open(cwd+'/financials_{}.csv'.format(ticker),'a') as File:
                for row in rows3:
                    prnt = row.get_text(separator='|').replace(",","")
                    doc = csv.writer(File)
                    doc.writerow(prnt.split('|'))
                File.close()
        url4 = 'https://in.finance.yahoo.com/quote/'+ticker+'/key-statistics?p='+ticker
        page4 = requests.get(url4)
        contents4 = page4.content
        soup4 = BeautifulSoup(contents4, 'html.parser')
        tabl4 = soup4.findAll("table", {"class": "table-qsp-stats Mt(10px)"})
        for t4 in tabl4:
            rows4 = t4.findAll('tr')
            with open(cwd+'/financials_{}.csv'.format(ticker),'a') as File:
                for row in rows4:
                    prnt = row.get_text(separator='|').replace(",","")
                    doc = csv.writer(File)
                    doc.writerow(prnt.split('|'))
                File.close()
    except:
        print("unable to extract data for ",ticker)
        continue
    
# extracting stock data (historical close price) for the stocks identified
close_prices = pd.DataFrame()
cp_tickers = all_tickers
attempt = 0
drop = []
while len(cp_tickers) != 0 and attempt <=5:
    print("-----------------")
    print("attempt number ",attempt)
    print("-----------------")
    cp_tickers = [j for j in cp_tickers if j not in drop]
    for i in range(len(cp_tickers)):
        try:
            temp = pdr.get_data_yahoo(cp_tickers[i],datetime.date.today()-datetime.timedelta(1825),datetime.date.today())
            temp.dropna(inplace = True)
            close_prices[cp_tickers[i]] = temp["Adj Close"]
            drop.append(cp_tickers[i])       
        except:
            print(cp_tickers[i]," :failed to fetch data...retrying")
            continue
    attempt+=1

# Export extracted stock data into a csv for future reproduction
close_prices.to_csv(cwd+"/closing_prices.csv") 