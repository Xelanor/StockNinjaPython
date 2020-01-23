import requests
from datetime import datetime, timedelta

from constants.tickers import tickers
import json
import utils


def calculate_and_record():
    data_scope = 1

    for ticker in tickers:
        historic_data = utils.get_stock_historic_data(ticker, data_scope)

        rsi = utils.calculate_rsi_index(historic_data, data_scope)[0]
        ninja = utils.calculate_ninja_index(historic_data, data_scope)[0]

        requests.post("http://34.67.211.44/api/ticker/add",
                      {"name": ticker, "rsi": rsi, "ninja": ninja})


def result(event, context):
    calculate_and_record()

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type, authorization",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': json.dumps("DONE")
    }
