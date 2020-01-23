import requests
import json
import random
import utils


def my_tickers_target_reminder(stock_names, stock_targets):

    QUERY_URL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols={}"

    stock_names = ",".join(stock_names)

    res = requests.get(QUERY_URL.format(stock_names))
    datas = res.json()["quoteResponse"]["result"]

    stocks_to_send = ["--- Günlük Hatırlatma ---\n", "Merhaba", "\n\n"]

    for data in datas:
        stock_name = data['symbol']

        for target in stock_targets:
            target_name = target["name"]

            if target_name == stock_name:
                try:
                    buyTarget = target["buyTarget"] if "buyTarget" in target else 0
                    sellTarget = target["sellTarget"] if "sellTarget" in target else 0
                    prevBuyTarget = target["prevBuyTarget"] if "prevBuyTarget" in target else 0
                    prevSellTarget = target["prevSellTarget"] if "prevSellTarget" in target else 0

                    current_price = data['regularMarketPrice']

                    stocks_to_send.append("{}\nAlış hd: {} Satış hd: {} Şuan: {}\n\n".format(
                        stock_name[:-3], buyTarget, sellTarget, current_price))
                except:
                    pass

    if len(stocks_to_send) != 3:
        stocks_to_send.append(
            "\nHedeflerini mobil uygulama üzerinden değiştirebilirsin.")
        utils.telegram_bot_sendtext("".join(stocks_to_send))
    else:
        stocks_to_send.append(
            "Bugün için hiç hedefin yok.")
        utils.telegram_bot_sendtext(",".join(stocks_to_send))


def result(event, context):
    stocks, data = utils.get_my_stocks()
    my_tickers_target_reminder(stocks, data)

    return {
        'statusCode': 200,
    }
