import requests
from datetime import datetime
import json
import utils


inform_rates = {
    0: 0.015,
    1: 0.02,
    2: 0.025,
    3: 0.03,
}


def invetment_inform(id, informCount):
    requests.post(
        "http://34.67.211.44/api/transaction/set-inform-number", {"id": id, "informCount": informCount})


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
        informCount = investment["informCount"]
        current_price = prices[stock_name]

        if informCount > 3:
            break

        inform_rate = inform_rates[informCount]

        if investment_type == "buy":
            if current_price > investment_price * (1 + inform_rate):
                message = "{}\n{}\nALIŞ\nAlış fiyatı: {}\nŞuanki fiyat: {}\n%{} üzerine çıktı.".format(
                    date, stock_name, investment_price, current_price, inform_rate * 100)
                utils.telegram_bot_sendtext(message)
                invetment_inform(transaction_id, informCount + 1)
            if current_price < investment_price * (1 - inform_rate):
                message = "{}\n{}\nALIŞ\nAlış fiyatı: {}\nŞuanki fiyat: {}\n%{} altına indi.".format(
                    date, stock_name, investment_price, current_price, inform_rate * 100)
                utils.telegram_bot_sendtext(message)
                invetment_inform(transaction_id, informCount + 1)
        if investment_type == "sell":
            if current_price < investment_price * (1 - inform_rate):
                message = "{}\n{}\nSATIŞ\nSatış fiyatı: {}\nŞuanki fiyat: {}\n%{} altına indi.".format(
                    date, stock_name, investment_price, current_price, inform_rate * 100)
                utils.telegram_bot_sendtext(message)
                invetment_inform(transaction_id, informCount + 1)


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


if __name__ == '__main__':
    output = result("", "")
    print(output["body"])
