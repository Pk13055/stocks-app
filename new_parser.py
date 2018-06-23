#!/usr/bin/env python3
"""
@author Mayank Rasu
@description Picking value stocks by web scraping company fundamental data based on
Greenblatt's Magic Formula
"""
import csv
import os
from multiprocessing import Pool

import pandas as pd
import requests
from bs4 import BeautifulSoup

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

DUMP_DIR = os.path.join(os.getcwd(), 'dumps')
fullpath = lambda x: os.path.join(DUMP_DIR, x)
try:
    os.mkdir(DUMP_DIR)
except:
    pass


def dumpLink(url, classes, ticker):
        '''
            @description Dumps the link to a file
            @param url -> str: url to parse
            @param classes -> str: classes for the table
            @param ticker -> str: the ticker for the url
            @return None
        '''
        url = url % (ticker, ticker)
        print("processing %s => %s" % (ticker, url), end="\r", flush=True)
        page = requests.get(url)
        contents = page.content
        soup = BeautifulSoup(contents, 'html.parser')
        tabl = soup.findAll("table", {"class": "Lh(1.7) W(100%) M(0)"})
        for t in tabl:
            rows = t.findAll('tr')
            f = open(fullpath('financials_{}.csv'.format(ticker)),'a+')
            for row in rows:
                prnt = row.get_text(separator='|').replace(",","")
                doc = csv.writer(f)
                doc.writerow(prnt.split('|'))
            f.close()

def createCSV(tickers):
    '''
        @description Creates the CSVs from uRLs specified
        @param tickers -> list: list of tickers to process for data
        @return None
    '''

    urls = [
        ('https://in.finance.yahoo.com/quote/%s/balance-sheet?p=%s',"Lh(1.7) W(100%) M(0)"),
        ('https://in.finance.yahoo.com/quote/%s/financials?p=%s',"Lh(1.7) W(100%) M(0)"),
        ('https://in.finance.yahoo.com/quote/%s/cash-flow?p=%s',"Lh(1.7) W(100%) M(0)"),
        ('https://in.finance.yahoo.com/quote/%s/key-statistics?p=%s',"table-qsp-stats Mt(10px)"),
    ]

    inps = [(url, cur_class, ticker) for ticker in tickers for url, cur_class in urls]
    Pool(8).starmap_async(dumpLink, inps).get()


def createStats():
    '''
        @description Creates the stats DataFrame from all the dumped CSVs
        @return all_stats_df -> pandas.DataFrame: Dataframe containing all
        the stats for the tickers dumped
    '''
    # creating dataframe with relevant financial information for each stock using
    # fundamental data exctracted through web scraping
    stats = [
        "Earnings before interest and taxes",
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
        "Forward annual dividend yield"
    ] # change as required

    indx = ["EBIT","MarketCap","NetIncome","CashFlowOps","Capex","CurrAsset",
            "CurrLiab","PPE","BookValue","TotDebt","PrefStock","DivYield"]
    all_stats = {}
    for ticker in tickers:
        temp = pd.read_csv(fullpath('financials_{}.csv'.format(ticker)))
        temp.set_index("Period ending",inplace=True)
        temp.drop(["Revenue","Period ending"],inplace=True)
        ticker_stats = []
        for stat in stats:
            if stat in "Market cap (intra-day)" or stat in "Forward annual dividend yield":
                ticker_stats.append(temp.loc[stat][2])
            else:
                ticker_stats.append(temp.loc[stat][0])
        all_stats[ticker] = ticker_stats
    all_stats_df = pd.DataFrame(all_stats,index=indx)

    # cleansing of fundamental data imported in dataframe
    all_stats_df.iloc[1,:] = [x.replace("M","E+03") for x in all_stats_df.iloc[1,:].values]
    all_stats_df.iloc[1,:] = [x.replace("B","E+06") for x in all_stats_df.iloc[1,:].values]
    all_stats_df.iloc[1,:] = [x.replace("T","E+09") for x in all_stats_df.iloc[1,:].values]
    all_stats_df.iloc[-1,:] = [str(x).replace("%","E-02") for x in all_stats_df.iloc[-1,:].values]
    for ticker in all_stats_df.columns:
        all_stats_df[ticker] = pd.to_numeric(all_stats_df[ticker].values,errors='coerce')

    return all_stats_df


def createFinalDF(all_stats_df):
    '''
        @description Creates the final data frame for
        the various tables
        @param all_stats_df -> pandas.DataFrame: the stats
        for all the stocks
        @return final_stats_df -> pandas.DataFrame: the calc.
        stats only for a couple of picked stocks
    '''
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


def createTables(final_stats_df):
    '''
        @description Finally creates the various dataframes
        required for rendering
        @param final_stats_df -> pandas.DataFrame: the stats for
        all the stocks
        @return
            - value_stocks -> pandas.DataFrame
            - high_dividend_stocks -> pandas.DataFrame
            - combined_stocks -> pandas.DataFrame
    '''

    # finding value stocks based on Magic Formula
    final_stats_df["CombRank"] = final_stats_df["EarningYield"].rank(ascending=False)+final_stats_df["ROC"].rank(ascending=False)
    value_stocks = final_stats_df.sort_values("CombRank").iloc[:round(0.1*len(all_stats_df.columns)),[2,4,5]]


    # finding highest dividend yield stocks
    high_dividend_stocks = final_stats_df.sort_values("DivYield",ascending=False).iloc[:round(0.1*len(all_stats_df.columns)),6]


    # # Magic Formula & Dividend yield combined
    final_stats_df["CombRank2"] = final_stats_df["EarningYield"].rank(ascending=False) \
                                +final_stats_df["ROC"].rank(ascending=False)  \
                                +final_stats_df["DivYield"].rank(ascending=False)
    combined_stocks = final_stats_df.sort_values("CombRank2").iloc[:round(0.1*len(all_stats_df.columns)),[2,4,6,5]]

    return value_stocks, high_dividend_stocks, combined_stocks


def main():
    createCSV(tickers)
    all_stats_df = createStats()
    final_stats_df = createFinalDF(all_stats_df)
    value_stocks, high_dividend_stocks, value_high_div_stocks = createTables(final_stats_df)
    # pickle files
    value_stocks.to_pickle("/value_stocks.pkl")
    high_dividend_stocks.to_pickle("/high_div.pkl")
    value_high_div_stocks.to_pickle("/value_high_div.pkl")


if __name__ == "__main__":
    main()
