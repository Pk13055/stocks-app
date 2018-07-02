#!/usr/bin/env python3
"""
Picking value stocks by web scraping company fundamental data based on
Greenblatt's Magic Formula
to be run everyday as 7:30PM IST

Author   - Mayank Rasu
"""

# importing libraries
import os
import requests
import pandas as pd

DATA_DIR = os.path.join(os.getcwd(), 'dumps')
try:
    os.mkdir(DATA_DIR)
except:
    pass

# the full path for the csv dumps
fullpath = lambda filename: os.path.join(DATA_DIR, filename)
# Fetches the latest list of tickers from gist
getTickers = lambda url: requests.get(url).text.splitlines()

all_tickers = getTickers(("https://gist.githubusercontent.com/mayankrasu/"
"8fe09d3a12ee9f0530a43886e2da1615/raw/all_tickers.txt"))

tickers_nonFI = getTickers(("https://gist.githubusercontent.com/mayankrasu/"
"8fe09d3a12ee9f0530a43886e2da1615/raw/tickers_nonFI.txt"))

# creating dataframe with relevant financial information for each stock using fundamental data
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
for ticker in all_tickers:
    try:
        temp = pd.read_csv(fullpath('financials_{}.csv'.format(ticker)))
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
final_stats_val_df = final_stats_df.loc[tickers_nonFI,:]
final_stats_val_df["CombRank"] = final_stats_val_df["EarningYield"].rank(ascending=False,na_option='bottom')+final_stats_val_df["ROC"].rank(ascending=False,na_option='bottom')
final_stats_val_df["MagicFormulaRank"] = final_stats_val_df["CombRank"].rank(method='first')
value_stocks = final_stats_val_df.sort_values("MagicFormulaRank").iloc[:round(0.1*len(all_stats_df.columns)),[2,4,5,8]]
print("------------------------------------------------")
print("Value stocks based on Greenblatt's Magic Formula")
print(value_stocks)


# finding highest dividend yield stocks
high_dividend_stocks = final_stats_df.sort_values("DivYield",ascending=False).iloc[:round(0.1*len(all_stats_df.columns)),6]
print("------------------------------------------------")
print("Highest dividend paying stocks")
print(high_dividend_stocks)


# # Magic Formula & Dividend yield combined
final_stats_df["CombRank"] = final_stats_df["EarningYield"].rank(ascending=False,method='first') \
                              +final_stats_df["ROC"].rank(ascending=False,method='first')  \
                              +final_stats_df["DivYield"].rank(ascending=False,method='first')
final_stats_df["CombinedRank"] = final_stats_df["CombRank"].rank(method='first')
value_high_div_stocks = final_stats_df.sort_values("CombinedRank").iloc[:round(0.1*len(all_stats_df.columns)),[2,4,6,5,8]]
print("------------------------------------------------")
print("Magic Formula and Dividend Yield combined")
print(value_high_div_stocks)


# pickle files
value_stocks.to_pickle('value_stocks.pkl')
high_dividend_stocks.to_pickle('high_div.pkl')
value_high_div_stocks.to_pickle('value_high_div.pkl')
