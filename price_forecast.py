"""
Forecasted price for major Indian stock indices
to be run everyday as 11:30 PM IST

Author   - Mayank Rasu
"""

import numpy as np
import pandas as pd
from yahoofinancials import YahooFinancials
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
import datetime
import os


cwd = os.getcwd()
all_tickers = ["^NSEI","^BSESN","^NSEBANK"]

# extracting historical close price for major stock indices
close_prices = pd.DataFrame()
end_date = (datetime.date.today()).strftime('%Y-%m-%d')
beg_date = (datetime.date.today()-datetime.timedelta(365)).strftime('%Y-%m-%d')
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
            yahoo_financials = YahooFinancials(cp_tickers[i])
            json_obj = yahoo_financials.get_historical_stock_data(beg_date,end_date,"daily")
            ohlv = json_obj[cp_tickers[i]]['prices']
            temp = pd.DataFrame(ohlv)[["formatted_date","adjclose"]]
            temp.set_index("formatted_date",inplace=True)
            temp2 = temp[~temp.index.duplicated(keep='last')]
            temp2.sort_index(axis=0,inplace=True)
            close_prices[cp_tickers[i]] = temp2["adjclose"]
            drop.append(cp_tickers[i])
        except:
            print(cp_tickers[i]," :failed to fetch data...retrying")
            continue
    attempt+=1

# function to perform Augmented Dickey Fuller test to check stationarity of data
def ADF(series):
    result = adfuller(series)
    print('ADF Statistic: %f' % result[0])
    print('p-value: %f' % result[1])
    print('Critical Values:')
    for key, value in result[4].items():
        print('\t%s: %.3f' % (key, value))
    if result[1] <= 0.05:
        print("********************************************")
        print("Unit root does not exist: Data is stationary")
    else:
        print("*************************************")
        print("Unit root exists: Data not stationary")

#################Making data stationary- Eliminating Trend#####################
# Log tranform and Differencing
close_price_log = np.log(close_prices)
moving_avg_log = close_price_log.rolling(window=10).mean()
differenced_data = close_price_log - moving_avg_log
differenced_data.dropna(inplace=True)
print("stationarity results for differenced assets")
for a in differenced_data.columns.values:
    result = adfuller(differenced_data[a])
    print("p value of ",a," is : %.8f" %result[1])
print("-------------------------------------------")


# Estimating best model fit using lowest AIC and BIC statistic
differenced_data.index = pd.DatetimeIndex(end=pd.datetime.today(), periods=len(differenced_data), freq='1D')

def aicbic(series):
    min_aic = 0
    aic_dict = {}
    for p in range(3):
        for d in range(3):
            for q in range(3):
                try:
                    temp = sm.tsa.ARIMA(series, (p,d,q)).fit().aic
                except:
                    temp = 0
                aic_dict[(p,d,q)] = temp
                if temp<min_aic:
                    min_aic = temp
                    min_key_aic = (p,d,q)
    min_bic = 0
    bic_dict = {}
    for p in range(3):
        for d in range(3):
            for q in range(3):
                try:
                    temp = sm.tsa.ARIMA(series, (p,d,q)).fit().bic
                except:
                    temp = 0
                bic_dict[(p,d,q)] = temp
                if temp<min_bic:
                    min_bic = temp
                    min_key_bic = (p,d,q)
    return [min_key_aic,min_key_bic]

forecast = []
for b in differenced_data.columns.values:
    print("---------------------",b,"-----------------------------")
    aic_bic = aicbic(differenced_data[b])
    arima_model_aic=sm.tsa.ARIMA(differenced_data[b], aic_bic[0]).fit()
    arima_model_bic=sm.tsa.ARIMA(differenced_data[b], aic_bic[1]).fit()
    output_aic = arima_model_aic.predict(start = len(differenced_data[b]), end = len(differenced_data[b]) + 2)
    output_bic = arima_model_bic.predict(start = len(differenced_data[b]), end = len(differenced_data[b]) + 2)
    output = (output_aic + output_bic)/2
    forecasted_price_1d_log = (10*output[0] + sum(close_price_log[b][-10:-1]))/9
    forecasted_price_1d = np.exp(forecasted_price_1d_log)
    forecast.append(forecasted_price_1d)
    print("--------------------------------------------------------")

    
forecast_df = pd.DataFrame({"ClosePrice":close_prices.iloc[-1,:].values,"NextForecastClose":forecast},index=["Nifty50","Sensex","NiftyBank"])

# pickle files
forecast_df.to_pickle(cwd+"/price_forecast.pkl")