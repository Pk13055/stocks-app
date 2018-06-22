"""
Picking value stocks by web scraping company fundamental data based on 
Greenblatt's Magic Formula

Author   - Mayank Rasu
"""

# importing libraries
import requests
import csv
from bs4 import BeautifulSoup
import os
import pandas as pd

cwd = os.getcwd() # getting current working directory to save output files


tickers = ["ZEEL.NS","WOCKPHARMA.NS","WIPRO.NS","VOLTAS.NS","VEDL.NS","VAKRANGEE.NS",
           "VGUARD.NS","MCDOWELL-N.NS","UBL.NS","ULTRACEMCO.NS","UPL.NS","TORNTPOWER.NS",
           "TORNTPHARM.NS","TITAN.NS","RAMCOCEM.NS","TECHM.NS","TATASTEEL.NS",
           "TATAPOWER.NS","TATAMOTORS.NS","TATAMTRDVR.NS","TATAGLOBAL.NS","TCS.NS",
           "TATACOMM.NS","TATACHEM.NS","TVSMOTOR.NS","TV18BRDCST.NS","SYNGENE.NS",
           "SUZLON.NS","SUNTV.NS","SUNPHARMA.NS","SPARC.NS","STRTECH.NS","SAIL.NS",
           "SIEMENS.NS","SHREECEM.NS","SRF.NS","RPOWER.NS","RELINFRA.NS","RELIANCE.NS",
           "RAJESHEXPO.NS","PGHH.NS","PRESTIGE.NS","POWERGRID.NS","PEL.NS","PIDILITIND.NS",
           "PETRONET.NS","PAGEIND.NS","PIIND.NS","PCJEWELLER.NS","OFSS.NS","OIL.NS",
           "ONGC.NS","OBEROIRLTY.NS","NATIONALUM.NS","NTPC.NS","NMDC.NS","NHPC.NS",
           "NBCC.NS","NATCOPHARM.NS","MPHASIS.NS","MOTHERSUMI.NS","MINDTREE.NS",
           "MARUTI.NS","MARICO.NS","MRPL.NS","M&M.NS","MGL.NS","MRF.NS","LUPIN.NS",
           "LT.NS","JUBILANT.NS","JUBLFOOD.NS","JINDALSTEL.NS","JSWSTEEL.NS",
           "JSWENERGY.NS","INDIGO.NS","INFY.NS","NAUKRI.NS","IGL.NS","IOC.NS",
           "INDHOTEL.NS","IBREALEST.NS","IDEA.NS","IRB.NS","ITC.NS","HINDZINC.NS",
           "HINDUNILVR.NS","HINDPETRO.NS","HINDALCO.NS","HEXAWARE.NS","HEROMOTOCO.NS",
           "HAVELLS.NS","HCLTECH.NS","GSPL.NS","GRASIM.NS","GODREJIND.NS","GODREJCP.NS",
           "GODREJAGRO.NS","GLENMARK.NS","GMRINFRA.NS","GAIL.NS","FCONSUMER.NS",
           "EXIDEIND.NS","ENGINERSIN.NS","ENDURANCE.NS","EMAMILTD.NS","EICHERMOT.NS",
           "DRREDDY.NS","DIVISLAB.NS","DISHTV.NS","DBL.NS","DABUR.NS","DLF.NS",
           "CUMMINSIND.NS","CROMPTON.NS","COROMANDEL.NS","CONCOR.NS","COLPAL.NS",
           "COALINDIA.NS","CIPLA.NS","CENTURYTEX.NS","CASTROLIND.NS","CADILAHC.NS",
           "BRITANNIA.NS","BOSCHLTD.NS","BIOCON.NS","INFRATEL.NS","BHARTIARTL.NS",
           "BPCL.NS","BHEL.NS","BHARATFORG.NS","BEL.NS","BERGEPAINT.NS","BATAINDIA.NS",
           "BALKRISIND.NS","BAJAJ-AUTO.NS","DMART.NS","AUROPHARMA.NS","ASIANPAINT.NS",
           "ASHOKLEY.NS","ARVIND.NS","APOLLOTYRE.NS","APOLLOHOSP.NS","AMBUJACEM.NS",
           "AMARAJABAT.NS","ALKEM.NS","AJANTPHARM.NS","ABFRL.NS","ADANIPOWER.NS",
           "ADANIPORTS.NS","AIAENG.NS","ACC.NS","ABB.NS"]


##########Web scraping to extract relevant fundamental data for companies######
for ticker in tickers:
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
###############################################################################
###############################################################################

# creating dataframe with relevant financial information for each stock using
# fundamental data exctracted through web scraping
stats = ["Earnings before interest and taxes",
         "Market cap (intra-day)",
         "Net income applicable to common shares",
         "Total cash flow from operating activities",
         "Capital expenditure",
         "Total current assets",
         "Total current liabilities",
         "Property plant and equipment",
         "Total stockholder equity",
         "Long-term debt",
         "Preferred stock",
         "Forward annual dividend yield"] # change as required

indx = ["EBIT","MarketCap","NetIncome","CashFlowOps","Capex","CurrAsset",
        "CurrLiab","PPE","BookValue","TotDebt","PrefStock","DivYield"]
all_stats = {}
for ticker in tickers:
    try:
        temp = pd.read_csv(cwd+'/financials_{}.csv'.format(ticker))
        temp.set_index("Period ending",inplace=True)
        temp.drop(["Revenue","Period ending"],inplace=True)
        ticker_stats = []
        for stat in stats:
            if stat == "Market cap (intra-day)" or stat == "Forward annual dividend yield":
                ticker_stats.append(temp.loc[stat][2])
            else:
                ticker_stats.append(temp.loc[stat][0])
        all_stats['{}'.format(ticker)] = ticker_stats
    except:
        print("can't read data for ",ticker)
    
all_stats_df = pd.DataFrame(all_stats,index=indx)

# cleansing of fundamental data imported in dataframe
all_stats_df.iloc[1,:] = [x.replace("M","E+03") for x in all_stats_df.iloc[1,:].values]
all_stats_df.iloc[1,:] = [x.replace("B","E+06") for x in all_stats_df.iloc[1,:].values]
all_stats_df.iloc[1,:] = [x.replace("T","E+09") for x in all_stats_df.iloc[1,:].values]
all_stats_df.iloc[-1,:] = [str(x).replace("%","E-02") for x in all_stats_df.iloc[-1,:].values]
for ticker in all_stats_df.columns:
    all_stats_df[ticker] = pd.to_numeric(all_stats_df[ticker].values,errors='coerce')
    
# calculating relevant financial metrics for each stock    
transpose_df = all_stats_df.transpose()
final_stats_df = pd.DataFrame()
final_stats_df["EBIT"] = transpose_df["EBIT"]
final_stats_df["TEV"] =  transpose_df["MarketCap"].fillna(0) \
                         +transpose_df["TotDebt"].fillna(0) \
                         +transpose_df["PrefStock"].fillna(0) \
                         -(transpose_df["CurrAsset"].fillna(0)-transpose_df["CurrLiab"].fillna(0))    
final_stats_df["EarningYield"] =  final_stats_df["EBIT"]/final_stats_df["TEV"]   
final_stats_df["FCFYield"] = (transpose_df["CashFlowOps"]-transpose_df["Capex"])/transpose_df["MarketCap"]   
final_stats_df["ROC"]  = transpose_df["EBIT"]/(transpose_df["PPE"]+transpose_df["CurrAsset"]-transpose_df["CurrLiab"])  
final_stats_df["BookToMkt"] = transpose_df["BookValue"]/transpose_df["MarketCap"]
final_stats_df["DivYield"] = transpose_df["DivYield"]


################################Output Dataframes##############################

# finding value stocks based on Magic Formula  
final_stats_df["CombRank"] = final_stats_df["EarningYield"].rank(ascending=False)+final_stats_df["ROC"].rank(ascending=False)   
value_stocks = final_stats_df.sort_values("CombRank").iloc[:round(0.1*len(all_stats_df.columns)),[2,4,5]]
print("------------------------------------------------")
print("Value stocks based on Greenblatt's Magic Formula")
print(value_stocks)    


# finding highest dividend yield stocks
high_dividend_stocks = final_stats_df.sort_values("DivYield",ascending=False).iloc[:round(0.1*len(all_stats_df.columns)),6]
print("------------------------------------------------")
print("Highest dividend paying stocks")
print(high_dividend_stocks)


# # Magic Formula & Dividend yield combined
final_stats_df["CombRank2"] = final_stats_df["EarningYield"].rank(ascending=False) \
                              +final_stats_df["ROC"].rank(ascending=False)  \
                              +final_stats_df["DivYield"].rank(ascending=False) 
value_high_div_stocks = final_stats_df.sort_values("CombRank2").iloc[:round(0.1*len(all_stats_df.columns)),[2,4,6,5]]
print("------------------------------------------------")
print("Magic Formula and Dividend Yield combined")
print(value_high_div_stocks)    


# pickle files
value_stocks.to_pickle(cwd+"/value_stocks.pkl")
high_dividend_stocks.to_pickle(cwd+"/high_div.pkl")
value_high_div_stocks.to_pickle(cwd+"/value_high_div.pkl")