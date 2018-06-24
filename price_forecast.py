# =============================================================================
# Forecast Gold Prices Price Using ARIMA
# =============================================================================

# Import necesary libraries
import numpy as np
import pandas as pd
import pandas_datareader.data as pdr
from statsmodels.tsa.stattools import adfuller
import statsmodels.graphics.tsaplots as tsplt
import statsmodels.api as sm

# Download gold data for last ten years from Fred
gold_price = pdr.get_data_fred("GOLDAMGBD228NLBM","2007-12-08","2017-12-08")
gold_price.dropna(inplace = True)
gold_price.plot(title = "Historical Gold Price Per Ounce in USD")

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

ADF(gold_price["GOLDAMGBD228NLBM"]) # testing stationarity of data

#################Making data stationary- Eliminating Trend#####################
# Log tranform and Differencing
gold_price_log = np.log(gold_price["GOLDAMGBD228NLBM"]) 
moving_avg = pd.rolling_mean(gold_price_log,10)
differenced_data = gold_price_log - moving_avg
differenced_data.dropna(inplace=True)
differenced_data.plot(title = "Log transformed and differenced data")
ADF(differenced_data) # testing stationarity of data

############################Box Jenkins Methodology############################
# Plotting ACF and PACF
tsplt.plot_acf(differenced_data, lags = 100, zero = False)
tsplt.plot_pacf(differenced_data, lags = 100, zero = False)

# Estimating best model fit using lowest AIC and BIC statistic
differenced_data.index = pd.DatetimeIndex(end=pd.datetime.today(), periods=len(differenced_data), freq='1D')

min_aic = 0
aic_dict = {}
for p in range(3):
    for d in range(3):
        for q in range(3):
            try:
                temp = sm.tsa.ARIMA(differenced_data, (p,d,q)).fit().aic
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
                temp = sm.tsa.ARIMA(differenced_data, (p,d,q)).fit().bic
            except:
                temp = 0
            bic_dict[(p,d,q)] = temp
            if temp<min_bic:
                min_bic = temp
                min_key_bic = (p,d,q)


print("Lowest AIC value for p,d,q : ",min_key_aic)
print("Lowest BIC value for p,d,q : ",min_key_bic)


# Forecasting output using best fit ARIMA model
arima_model_aic=sm.tsa.ARIMA(differenced_data, min_key_aic).fit()
print("****************")
print("model parameters")
print("****************")
print(arima_model_aic.params)
print("********************")


arima_model_bic=sm.tsa.ARIMA(differenced_data, min_key_bic).fit()
print("****************")
print("model parameters")
print("****************")
print(arima_model_bic.params)
print("********************")



output_aic = arima_model_aic.predict(start = len(differenced_data), end = len(differenced_data) + 2)
output_bic = arima_model_bic.predict(start = len(differenced_data), end = len(differenced_data) + 2)
output = (output_aic + output_bic)/2
print(output)

# transforming forecasted output to gold price
forecasted_price_1d_log = (10*output[0] + sum(gold_price_log[-10:-1]))/9
forecasted_price_1d = np.exp(forecasted_price_1d_log)
print("Forecasted price in 1 day = %.2f" %forecasted_price_1d)
