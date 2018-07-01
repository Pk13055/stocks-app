import datetime
import json
import os
import pickle

import pandas as pd
import requests
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.

def test_route(request):
    '''
        @description Testing route
    '''
    table = pickle.load(open('value_stocks.pkl', 'rb'))
    return render(request, 'test.html.j2', context={
        'status' : True,
        'table' : table.to_html()
    })


def homepage_route(request):
    '''
        @description Main page of the website

    '''
    frames = [
        {
            'id' : "priceForecast",
            'name' : "Next Day Forecast",
            'icon' : 'trending_up',
            'data' : pickle.load(open('forecasted_prices.pkl', 'rb')),
            'last_modified' : datetime.datetime.fromtimestamp(os.path.getmtime('forecasted_prices.pkl')),

        },
        {
            'id' : "valueStocks",
            'name' : "Value Stocks",
            'icon' : 'attach_money',
            'data' : pickle.load(open('value_stocks.pkl', 'rb')),
            'last_modified' : datetime.datetime.fromtimestamp(os.path.getmtime('value_stocks.pkl')),

        },
        {
            'id' : "dividendStocks",
            'icon' : 'donut_small',
            'name' : "Dividend Stocks",
            'data' : pickle.load(open('high_div.pkl', 'rb')),
            'last_modified' : datetime.datetime.fromtimestamp(os.path.getmtime('high_div.pkl')),
        },
        {
            'id' : "combinedStocks",
            'icon' : 'call_merge',
            'name' : "Value and Dividend Combined",
            'data' : pickle.load(open('value_high_div.pkl', 'rb')),
            'last_modified' : datetime.datetime.fromtimestamp(os.path.getmtime('value_high_div.pkl')),
        },
        {
            'id' : "cointPairs",
            'icon' : 'compare_arrow',
            'name' : "Cointegrated Pairs",
            'data' : pickle.load(open('coint_pairs.pkl', 'rb')),
            'last_modified' : datetime.datetime.fromtimestamp(os.path.getmtime('coint_pairs.pkl')),
        }
    ]

    # Fetches the latest list of tickers from gist
    getGist = lambda url: requests.get(url).text.splitlines()

    # add the writeup and change data to HTML
    [_.update({
        'writeup' : writeup,
        'data' : pd.DataFrame(_['data']).to_html()
    }) for _, writeup in zip(frames, getGist(("https://gist.githubusercontent.com/mayankrasu/8fe09d3a12ee9f0530a43886e2da1615/raw/writeup.txt")))]
    return render(request, 'homepage.html.j2', context={
        'title' : "homepage",
        'records' : frames,
    })


def contact_route(request):
    '''
        @description contact page of the website

    '''
    return render(request, 'contact.html.j2', context={
        'title' : "contact",
    })


def method_route(request):
    '''
        @description The methodology page of the website
    '''

    methods = open('methods.txt').readlines()
    return render(request, 'methodology.html.j2', context={
        'title' : "methodology",
        'points' : methods,
    })
