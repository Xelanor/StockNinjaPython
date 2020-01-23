import requests
import json
import random
import utils


def check_stock_existence(stock):
    QUERY_URL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols={}"

    res = requests.get(QUERY_URL.format(stock))

    stock = res.json()["quoteResponse"]["result"]

    if stock == []:
        return False
    else:
        return True


def result(event, context):
    stock = event["queryStringParameters"]["name"]

    result = check_stock_existence(stock)

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type, authorization",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': json.dumps(result)
    }
