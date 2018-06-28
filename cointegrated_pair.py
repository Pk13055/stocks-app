#!/usr/bin/env python3
"""
Extracting relavent stock and fundamental data for relevant stocks
to be run every weekday at 8:30PM IST

Author   - Mayank Rasu
"""

# Import necesary libraries
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller
import os

cwd = os.getcwd() # getting current working directory to save output files

stocks = pd.read_csv(cwd+"/closing_prices.csv",index_col = "formatted_date")

# Function to standardize each column of a dataframe
def standardize_df(df):
    std_df = (df - df.mean(axis=0))/df.std(axis=0)
    return std_df

# Transformed dataframe
standardized_stocks = standardize_df(stocks)
standardized_stocks.fillna(method="bfill",limit=3,inplace=True)
standardized_stocks.dropna(axis=1,how="any",inplace=True)

# function to perform Augmented Dickey Fuller test to check stationarity of data
def ADF(series):
    result = adfuller(series)
    return result[1]

# Calculating ADF p-value for each stock pair difference
coint_dict = {}
for i in range(len(standardized_stocks.columns)):
    for j in range(i+1,len(standardized_stocks.columns)):
        i_j = '{}_{}'.format(i,j)
        coint_dict[i_j] = ADF(standardized_stocks.iloc[:,i]-standardized_stocks.iloc[:,j])

# Name mapping
name_map = {}
for i in range(len(standardized_stocks.columns)):
    for j in range(i+1,len(standardized_stocks.columns)):
        i_j = '{}_{}'.format(i,j)
        name_map[i_j] = standardized_stocks.columns[i]+"_"+standardized_stocks.columns[j]

# Dataframe with pairs having p-value above threshold
selected_pairs = pd.DataFrame()
for p in coint_dict:
    if coint_dict[p] <= 0.01: #99% CI; change this value as per the required significance level
        selected_pairs[name_map[p]] = [coint_dict[p]]

# Function to calculate signals and triggers based on current stock price
def trigger(stock1,stock2,stock1_stndz,stock2_stndz):
    linear_comb = stock1_stndz - stock2_stndz
    half_life = round((-np.log(2)/adfuller(linear_comb)[0])*252,0)
    upper_signal = round(np.percentile(linear_comb,97.5),1) #change the percentile level as per requirement
    lower_signal = round(np.percentile(linear_comb,2.5),1) #change the percentile level as per requirement
    present_ratio = stocks[stock1][-1]/stocks[stock2][-1]
    target_ratio = np.mean(stocks[stock1])/np.mean(stocks[stock2])
    actual = stock1_stndz[-1] - stock2_stndz[-1]
    if actual>upper_signal or actual<lower_signal:
        trigger = True
    else:
        trigger = False
    if trigger == False:
        message = "No Action"
    elif actual >= 0:
        message = "buy "+stock2+" sell "+stock1
    else:
        message = "buy "+stock1+" sell "+stock2

    return [trigger,lower_signal,upper_signal,actual,half_life,present_ratio,target_ratio,message]

# Printing out all relevant information for pairs of stock which show cointegration
title = ["Stock", "Close_Price_1", "Cointegrated_Stock", "Close_Price_2",
    "Action", "Half_Life", "Current_Ratio", "Expected_Ratio"]

final_df = pd.DataFrame()
for a in range(len(selected_pairs.columns)):
    stock_pair = list(selected_pairs)[a].split("_")
    output = trigger(stock_pair[0],stock_pair[1],standardized_stocks[stock_pair[0]],standardized_stocks[stock_pair[1]])
    if output[0]==True:
        temp_df = pd.DataFrame(data = [stock_pair[0],stocks[stock_pair[0]][-1],stock_pair[1],stocks[stock_pair[1]][-1],output[-1],output[4],output[5],output[6]], index = title)
        try:
            final_df = final_df.merge(temp_df, how='outer', left_index=True, right_index=True)
        except:
            final_df = temp_df
final_df = final_df.transpose()
final_df.set_index("Stock",inplace=True)
final_df.index.name = None

# pickle files
final_df.to_pickle(cwd+"/coint_pairs.pkl")
