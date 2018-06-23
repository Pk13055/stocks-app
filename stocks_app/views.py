import json
import pickle

import pandas as pd
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
            'id' : "valueStocks",
            'name' : "Value Stocks",
            'icon' : 'trending_up',
            'data' : pickle.load(open('value_stocks.pkl', 'rb')),
        },
        {
            'id' : "dividendStocks",
            'icon' : 'donut_small',
            'name' : "Dividend Stocks",
            'data' : pickle.load(open('high_div.pkl', 'rb')),
        },
        {
            'id' : "combinedStocks",
            'icon' : 'call_merge',
            'name' : "Value and Dividend Combined",
            'data' : pickle.load(open('value_high_div.pkl', 'rb')),
        },
        {
            'id' : "cointPairs",
            'icon' : 'compare_arrow',
            'name' : "Cointegrated Pairs",
            'data' : pickle.load(open('coint_pairs.pkl', 'rb')),
        }
    ]
    # add the writeup and change data to HTML
    [_.update({
        'writeup' : writeup,
        'data' : pd.DataFrame(_['data']).to_html()
    }) for _, writeup in zip(frames, open('writeups.txt').readlines())]
    return render(request, 'homepage.html.j2', context={
        'title' : "homepage",
        'records' : frames,
    })


def about_route(request):
    '''
        @description about page of the website

    '''
    return render(request, 'about.html.j2', context={
        'title' : "about us",
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
        @description Main page of the website

    '''
    return render(request, 'methodology.html.j2', context={
        'title' : "methodology",
    })
