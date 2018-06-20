#!/usr/bin/env python
"""
    @author Mayank Rasu
    @description Picking value stocks by web scraping
    company fundamental data based on Greenblatt's Magic Formula
"""
import csv
import os
import pickle
import random
import sys
from multiprocessing import Pool, Process

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

# CORE COUNT for optimum multiprocessing
CORE_COUNT = 4
# create the storage dirs
PICKLE_DIR = os.path.join(os.getcwd(), 'pickled')
DUMP_DIR = os.path.join(os.getcwd(), 'dumps')
try:
    os.mkdir(PICKLE_DIR)
    os.mkdir(DUMP_DIR)
except FileExistsError:
    pass

# ticker list for raw data retrieval
tickers = [
    "ZEEL.NS", "WOCKPHARMA.NS", "WIPRO.NS", "VOLTAS.NS", "VEDL.NS",
    "VAKRANGEE.NS", "VGUARD.NS", "MCDOWELL-N.NS", "UBL.NS", "ULTRACEMCO.NS",
    "UPL.NS", "TORNTPOWER.NS", "TORNTPHARM.NS", "TITAN.NS", "RAMCOCEM.NS",
    "TECHM.NS", "TATASTEEL.NS", "TATAPOWER.NS", "TATAMOTORS.NS",
    "TATAMTRDVR.NS", "TATAGLOBAL.NS", "TCS.NS", "TATACOMM.NS", "TATACHEM.NS",
    "TVSMOTOR.NS", "TV18BRDCST.NS", "SYNGENE.NS", "SUZLON.NS", "SUNTV.NS",
    "SUNPHARMA.NS", "SPARC.NS", "STRTECH.NS", "SAIL.NS", "SIEMENS.NS",
    "SHREECEM.NS", "SRF.NS", "RPOWER.NS", "RELINFRA.NS", "RELIANCE.NS",
    "RAJESHEXPO.NS", "PGHH.NS", "PRESTIGE.NS", "POWERGRID.NS", "PEL.NS",
    "PIDILITIND.NS", "PETRONET.NS", "PAGEIND.NS", "PIIND.NS", "PCJEWELLER.NS",
    "OFSS.NS", "OIL.NS", "ONGC.NS", "OBEROIRLTY.NS", "NATIONALUM.NS", "NTPC.NS",
    "NMDC.NS", "NHPC.NS", "NBCC.NS", "NATCOPHARM.NS", "MPHASIS.NS",
    "MOTHERSUMI.NS", "MINDTREE.NS", "MARUTI.NS", "MARICO.NS", "MRPL.NS",
    "M&M.NS", "MGL.NS", "MRF.NS", "LUPIN.NS", "LT.NS", "JUBILANT.NS",
    "JUBLFOOD.NS", "JINDALSTEL.NS", "JSWSTEEL.NS", "JSWENERGY.NS", "INDIGO.NS",
    "INFY.NS", "NAUKRI.NS", "IGL.NS", "IOC.NS", "INDHOTEL.NS", "IBREALEST.NS",
    "IDEA.NS", "IRB.NS", "ITC.NS", "HINDZINC.NS", "HINDUNILVR.NS",
    "HINDPETRO.NS", "HINDALCO.NS", "HEXAWARE.NS", "HEROMOTOCO.NS", "HAVELLS.NS",
    "HCLTECH.NS", "GSPL.NS", "GRASIM.NS", "GODREJIND.NS", "GODREJCP.NS",
    "GODREJAGRO.NS", "GLENMARK.NS", "GMRINFRA.NS", "GAIL.NS", "FCONSUMER.NS",
    "EXIDEIND.NS", "ENGINERSIN.NS", "ENDURANCE.NS", "EMAMILTD.NS",
    "EICHERMOT.NS", "DRREDDY.NS", "DIVISLAB.NS", "DISHTV.NS", "DBL.NS",
    "DABUR.NS", "DLF.NS", "CUMMINSIND.NS", "CROMPTON.NS", "COROMANDEL.NS",
    "CONCOR.NS", "COLPAL.NS", "COALINDIA.NS", "CIPLA.NS", "CENTURYTEX.NS",
    "CASTROLIND.NS", "CADILAHC.NS", "BRITANNIA.NS", "BOSCHLTD.NS", "BIOCON.NS",
    "INFRATEL.NS", "BHARTIARTL.NS", "BPCL.NS", "BHEL.NS", "BHARATFORG.NS",
    "BEL.NS", "BERGEPAINT.NS", "BATAINDIA.NS", "BALKRISIND.NS", "BAJAJ-AUTO.NS",
    "DMART.NS", "AUROPHARMA.NS", "ASIANPAINT.NS", "ASHOKLEY.NS", "ARVIND.NS",
    "APOLLOTYRE.NS", "APOLLOHOSP.NS", "AMBUJACEM.NS", "AMARAJABAT.NS",
    "ALKEM.NS", "AJANTPHARM.NS", "ABFRL.NS", "ADANIPOWER.NS", "ADANIPORTS.NS",
    "AIAENG.NS", "ACC.NS", "ABB.NS"
]

def getContent(url):
    try:
        return requests.get(url, timeout=5).text
    except requests.exceptions.ConnectionError as e:
        print("Rate limiting! %s" % e)
        import time
        time.sleep(30)
        getContent(url)


def dumpContent(tickers):
    '''
        @description fetches the subset of tickers using a resource pool
        and writes it to a file
        @param tickers -> list: smaller list of tickers
        @return None
    '''
    def dumpTicker(ticker):
        '''
            @description Dumps a ticker to a pickle file for later
            parsing
            @param ticker -> str: ticker to be processed
        '''
        urls = [
            'https://in.finance.yahoo.com/quote/%s/balance-sheet?p=%s',
            'https://in.finance.yahoo.com/quote/%s/financials?p=%s',
            'https://in.finance.yahoo.com/quote/%s/cash-flow?p=%s',
            'https://in.finance.yahoo.com/quote/%s/key-statistics?p=%s',
        ]

        print("Processing %s" % ticker, end="\r")
        pool = Pool(2 * CORE_COUNT)
        raw_list = pool.map_async(getContent, list(map(lambda _: _ % (ticker, ticker), urls))).get()
        content = ''.join(list(map(lambda x: x if x is not None else '', raw_list)))
        pool.close()
        open(os.path.join(PICKLE_DIR, '%s_raw.html' % ticker), 'w').write(content)

    [dumpTicker(_) for _ in tickers]


def fetchRawContent(tickers):
    '''
        @description async get the page contents for bs4 processing
        @param tickers -> list: list of tickers to retrieve
        @return None
    '''
    random.shuffle(tickers)
    PROCESSES = CORE_COUNT # number of processes to use for the request getting
    idxs = [_ for _ in range(0, len(tickers), round(len(tickers) / PROCESSES))] + [len(tickers)]
    split_ticks = [tickers[idxs[_]:idxs[_ + 1]] for _ in range(len(idxs) - 1)]
    processes = [Process(target=dumpContent, args=(_,)) for _ in split_ticks]
    [_.start() for _ in processes]
    [_.join() for _ in processes]


def dumpCSV(content, ticker):
    '''
        @description Given HTML content,
        this will dump the generated csv
        @param content -> str: HTML string
        @param ticker -> str: Ticker name
        @return None
    '''
    print("Generating csv %s" % ticker, end="\r", flush=True)
    classes = [
        "Lh(1.7) W(100%) M(0)",
        "table-qsp-stats Mt(10px)",
    ]
    soup = BeautifulSoup(content, 'html.parser')
    tabl = soup.findAll("table", { "class": classes })
    for t in tabl:
        rows = t.findAll('tr')
        f = open(os.path.join(DUMP_DIR, 'financials_%s.csv' % (ticker)), 'a+')
        for row in rows:
            prnt = row.get_text(separator='|').replace(",", "")
            doc = csv.writer(f)
            doc.writerow(prnt.split('|'))
        f.close()


def populate_store():
    '''
        @description parses various url tickers and extracts
        relevant information (stores to csv)
        @return None
    '''

    # Obselete, dumping to txt first
    urls = [
        ('https://in.finance.yahoo.com/quote/%s/balance-sheet?p=%s', "Lh(1.7) W(100%) M(0)"),
        ('https://in.finance.yahoo.com/quote/%s/financials?p=%s', "Lh(1.7) W(100%) M(0)"),
        ('https://in.finance.yahoo.com/quote/%s/cash-flow?p=%s', "Lh(1.7) W(100%) M(0)"),
        ('https://in.finance.yahoo.com/quote/%s/key-statistics?p=%s', "table-qsp-stats Mt(10px)"),
    ]

    fetchRawContent(tickers)
    contents = []
    for ticker in tickers:
        try:
            content = open(os.path.join(PICKLE_DIR, '%s_raw.html' % ticker)).read()
            contents.append((content, ticker))
        except FileNotFoundError:
            print("Error retrieving %s! Skipping" % ticker, end="\r", flush=True)
            continue
    pool = Pool(2 * CORE_COUNT)
    pool.starmap_async(dumpCSV, contents).get()


def createBaseDF(all_stats, index):
    '''
        @description Creates the data frame for the formatted
        data given a dict
        @param all_stats -> dict: the dictionary containing the data
        @param index -> list: list of the indices (columns)
        @return df -> pd.DataFrame: the final dataframe
    '''
    all_stats_df = pd.DataFrame(all_stats, index=index)
    # cleansing of fundamental data imported in dataframe
    all_stats_df.iloc[1, :]=[x.replace("B", "E+06") for x in all_stats_df.iloc[1, :].values]
    all_stats_df.iloc[1, :]=[x.replace("T", "E+09") for x in all_stats_df.iloc[1, :].values]
    for ticker in all_stats_df.columns:
        all_stats_df[ticker][:-1]=pd.to_numeric(all_stats_df[ticker].values[:-1], errors='coerce')
    return all_stats_df


def getFinalDF(all_stats_df):
    '''
        @description Creates the final dataframe after calculation
        @param all_stats_df -> pd.DataFrame: all_stats DataFrame
        @return final_stats_df -> pd.DataFrame: Calculated df
    '''
    final_stats_df = pd.DataFrame()
    transpose_df= all_stats_df.transpose()

    final_stats_df["EBIT"] = transpose_df["EBIT"]

    final_stats_df["TEV"] = transpose_df["MarketCap"].fillna(0) \
    + transpose_df["TotDebt"].fillna(0) \
    + transpose_df["PrefStock"].fillna(0)   \
    - (transpose_df["CurrAsset"].fillna(0)  \
    - transpose_df["CurrLiab"].fillna(0))

    final_stats_df["EarningYield"] =  final_stats_df["EBIT"] / final_stats_df["TEV"]
    final_stats_df["FCFYield"] = (transpose_df["CashFlowOps"] - transpose_df["Capex"]) / transpose_df["MarketCap"]
    final_stats_df["ROC"] = transpose_df["EBIT"] / (transpose_df["PPE"] + transpose_df["CurrAsset"] - transpose_df["CurrLiab"])
    final_stats_df["BookToMkt"] = transpose_df["BookValue"] / transpose_df["MarketCap"]
    final_stats_df["DivYield"] = transpose_df["DivYield"]
    return final_stats_df


def findValueStocks(final_stats_df, all_stats_df):
    '''
        @description Finally finds the value and high dividend stocks
        on the basis of the final dataframe
        @param final_stats_df -> pd.DataFrame: final stats aggregated
        @return (value_stocks, high_dividend_stocks) -> tuple(list, list):
            Final value and high dividend stocks
    '''
    # finding value stocks based on Magic Formula
    final_stats_df["CombRank"] = final_stats_df["EarningYield"].rank(
    ascending=False) + final_stats_df["ROC"].rank(ascending=False)
    value_stocks = final_stats_df.sort_values(
    "CombRank").iloc[:round(0.1 * len(all_stats_df.columns)), [2, 4, 5]]

    # finding highest dividend yield stocks
    high_dividend_stocks = final_stats_df.sort_values(
    "DivYield", ascending=False).iloc[:round(0.1 * len(all_stats_df.columns)), -2]

    return value_stocks, high_dividend_stocks


def main():
    '''
        @description main function that ties everything together
        @return None
    '''
    populate_store() # create the csv files for processing

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
            "Forward annual dividend yield"]  # change as required

    # relevant indices to query
    indx=["EBIT", "MarketCap", "NetIncome", "CashFlowOps", "Capex", "CurrAsset",
        "CurrLiab", "PPE", "BookValue", "TotDebt", "PrefStock", "DivYield"]

    # read the generated csvs to prepare the dataframe
    all_stats={}
    for ticker in tickers:
        try:
            temp = pd.read_csv(os.path.join(DUMP_DIR, 'financials_%s.csv' % (ticker)))
        except Exception as e:
            print("CSV not generated %s! Skipping! %s" % (ticker, e), end="\r", flush=True)
            continue
        temp.set_index("Period ending", inplace=True)
        temp.drop(["Revenue", "Period ending"], inplace=True)
        ticker_stats=[ temp.loc[stat][2 if stat == "Market cap (intra-day)" or
            stat == "Forward annual dividend yield" else 0] for stat in stats]
        all_stats['%s' % ticker] = ticker_stats

    all_stats_df = createBaseDF(all_stats, indx)
    final_stats_df = getFinalDF(all_stats_df)
    value_stocks, high_dividend_stocks = findValueStocks(final_stats_df, all_stats_df)

    print(50 * "-", "Value stocks based on Greenblatt's Magic Formula", value_stocks, sep="\n")
    print(50 * "-", "Highest dividend paying stocks", high_dividend_stocks, sep="\n")


# call the main function from the cmd
if __name__ == "__main__":
    main()
