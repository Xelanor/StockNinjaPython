import requests
from datetime import datetime
import json
import utils


def invetment_inform(id):
    requests.post(
        "http://34.67.211.44/api/transaction/set-informed", {"id": id})


def investment_tracker():
    tickers_buy = []
    tickers_sell = []
    unique_investments = []

    QUERY_URL = "http://34.67.211.44/api/transaction"

    res = requests.get(QUERY_URL)
    transactions = res.json()

    for transaction in transactions:
        name = transaction['name']
        t_type = transaction['type']
        if t_type == "buy":
            if name not in tickers_buy:
                unique_investments.append(transaction)
                tickers_buy.append(name)
        else:
            if name not in tickers_sell:
                unique_investments.append(transaction)
                tickers_sell.append(name)

    tickers = list(set(tickers_buy + tickers_sell))
    prices = utils.get_prices(tickers)

    for investment in unique_investments:
        investment_price = float(investment["price"])
        stock_name = investment["name"]
        investment_type = investment["type"]
        date = datetime.strptime(
            investment["createdAt"][:10], "%Y-%m-%d").strftime("%d.%m.%Y")
        transaction_id = investment["_id"]
        informed = investment["informed"]
        current_price = prices[stock_name]

        if informed == True:
            break

        if investment_type == "buy":
            if current_price > investment_price * 1.02:
                message = "{}\n{}\nALIŞ\nAlış fiyatı: {}\nŞuanki fiyat: {}\n%2 üzerine çıktı.".format(
                    date, stock_name, investment_price, current_price)
                utils.telegram_bot_sendtext(message)
                invetment_inform(transaction_id)
            if current_price < investment_price * 0.98:
                message = "{}\n{}\nALIŞ\nAlış fiyatı: {}\nŞuanki fiyat: {}\n%2 altına indi.".format(
                    date, stock_name, investment_price, current_price)
                utils.telegram_bot_sendtext(message)
                invetment_inform(transaction_id)
        if investment_type == "sell":
            if current_price < investment_price * 0.98:
                message = "{}\n{}\nSATIŞ\nSatış fiyatı: {}\nŞuanki fiyat: {}\n%2 altına indi.".format(
                    date, stock_name, investment_price, current_price)
                utils.telegram_bot_sendtext(message)
                invetment_inform(transaction_id)


def result(event, context):
    investment_tracker()

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type, authorization",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': json.dumps("done")
    }
