#!/usr/bin/env python3
"""
Picking value stocks by web scraping company fundamental data based on
Greenblatt's Magic Formula
to be run everyday as 7:30PM IST

Author   - Mayank Rasu
"""

# importing libraries
import os
import pandas as pd

cwd = os.getcwd() # getting current working directory to save output files


tickers_nonFI = ["ZEEL.NS","WOCKPHARMA.NS","WIPRO.NS","VOLTAS.NS","VEDL.NS","VAKRANGEE.NS",
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

tickers_all = ["ZEEL.NS","YESBANK.NS","WOCKPHARMA.NS","WIPRO.NS","VOLTAS.NS","VEDL.NS",
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
for ticker in tickers_all:
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
final_stats_val_df = final_stats_df.loc[tickers_nonFI,:]
final_stats_val_df["CombRank"] = final_stats_val_df["EarningYield"].rank(ascending=False)+final_stats_val_df["ROC"].rank(ascending=False)
value_stocks = final_stats_val_df.sort_values("CombRank").iloc[:round(0.1*len(all_stats_df.columns)),[2,4,5]]
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