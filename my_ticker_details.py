import requests
from datetime import datetime, timedelta
import json
import utils


def my_ticker_details(stocks_targets):

    QUERY_URL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols={}"

    stock_names = []
    for stock in stocks_targets:
        stock_names.append(stock['name'])

    result = []

    stock_names.sort()

    stock_names = ",".join(stock_names)
    res = requests.get(QUERY_URL.format(stock_names))
    stocks_data = res.json()["quoteResponse"]["result"]

    for data_dict in stocks_data:
        stock_name = data_dict["symbol"]

        for target_dict in stocks_targets:

            if stock_name == target_dict['name']:

                price = data_dict["regularMarketPrice"]
                prevClose = data_dict["regularMarketPreviousClose"]

                rate = utils.rateCalculator(price, prevClose)

                stock_dict = {
                    "stockName": stock_name,
                    "date": utils.epoch_to_date(data_dict["regularMarketTime"]),
                    "price": data_dict["regularMarketPrice"],
                    "shortName": data_dict["shortName"],
                    "dayRange": data_dict["regularMarketDayRange"],
                    "rate": rate
                }

                result.append(stock_dict)

    return result


def result(event, context):
    _, stocks = utils.get_my_stocks()
    prices = my_ticker_details(stocks)

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type, authorization",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': json.dumps(prices)
    }
