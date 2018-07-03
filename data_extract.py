#!/usr/bin/env python3
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
from yahoofinancials import YahooFinancials
import datetime

DATA_DIR = os.path.join(os.getcwd(), 'dumps')
try:
    os.mkdir(DATA_DIR)
except:
    pass

# the full path for the csv dumps
fullpath = lambda filename: os.path.join(DATA_DIR, filename)
# Fetches the latest list of tickers from gist
getTickers = lambda url: requests.get(url).text.splitlines()

all_tickers = getTickers(("https://gist.githubusercontent.com/mayankrasu/8fe09d3a12ee9f0530a43886e2da1615/raw/all_tickers.txt"))

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
            with open(fullpath('financials_{}.csv'.format(ticker)),'w') as File:
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
            with open(fullpath('financials_{}.csv'.format(ticker)),'a') as File:
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
            with open(fullpath('financials_{}.csv'.format(ticker)),'a') as File:
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
            with open(fullpath('financials_{}.csv'.format(ticker)),'a') as File:
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
end_date = (datetime.date.today()+datetime.timedelta(1)).strftime('%Y-%m-%d')
beg_date = (datetime.date.today()-datetime.timedelta(1825)).strftime('%Y-%m-%d')
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
            temp2 = temp[~temp.index.duplicated(keep='first')]
            temp2.sort_index(axis=0,inplace=True)
            close_prices[cp_tickers[i]] = temp2["adjclose"]
            drop.append(cp_tickers[i])
        except:
            print(cp_tickers[i]," :failed to fetch data...retrying")
            continue
    attempt+=1

# Export extracted stock data into a csv for future reproduction
close_prices.to_csv("closing_prices.csv")
