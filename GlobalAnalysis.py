import requests
from datetime import datetime, timedelta

from StockDetails import StockDetails
from constants.tickers import tickers


def calculate_and_record():

    print(datetime.now())

    for ticker in tickers:
        stock_details = StockDetails(ticker, 1)
        stock_details.get_stock_historic_data()

        rsi = stock_details.calculate_rsi_index()[0]
        ninja = stock_details.calculate_ninja_index()[0]

        print(ticker)

        requests.post("http://34.67.211.44/api/ticker/add",
                      {"name": ticker, "rsi": rsi, "ninja": ninja})

    print(datetime.now())


def check_stock():
    stock_details = StockDetails('DENGE.IS', 1)
    stock_details.get_stock_historic_data()

    rsi = stock_details.calculate_rsi_index()[0]
    ninja = stock_details.calculate_ninja_index()[0]

    print(rsi, ninja)


stock_details = StockDetails("ARENA.IS", 1)
stock_details.get_stock_target()
