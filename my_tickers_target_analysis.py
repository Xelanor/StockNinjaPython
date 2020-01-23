import requests
import json
import random
import utils


def check_buy_target(target, price):
    target = target * 1.002 if target < 100 else target

    if target == 0:
        return False

    if float(price) <= target:
        return True
    return False


def check_sell_target(target, price):
    target = target * 0.998 if target < 100 else target

    if target == 0:
        return False

    if float(price) >= target:
        return True
    return False


def my_tickers_target_analysis(stock_names, stock_targets):

    QUERY_URL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols={}"

    stock_names = ",".join(stock_names)

    res = requests.get(QUERY_URL.format(stock_names))
    datas = res.json()["quoteResponse"]["result"]

    for data in datas:
        stock_name = data['symbol']

        for target in stock_targets:
            target_name = target["name"]

            if target_name == stock_name:
                try:
                    buyTarget = target["buyTarget"] if "buyTarget" in target else 0
                    sellTarget = target["sellTarget"] if "sellTarget" in target else 1000000000

                    current_price = data['regularMarketPrice']

                    if check_buy_target(buyTarget, current_price):
                        telegram_bot_sendtext("{} {} oldu senin ALIŞ hedefin {} Alabilirsin".format(
                            stock_name[:-3], current_price, buyTarget))
                        res = requests.post("https://teknodeneyim.com/stocks/setbuytarget", {
                                            "name": stock_name, "target": 0, "prevTarget": float(buyTarget)})

                    if check_sell_target(sellTarget, current_price):
                        telegram_bot_sendtext("{} {} oldu senin SATIŞ hedefin {} Satabilirsin".format(
                            stock_name[:-3], current_price, sellTarget))
                        res = requests.post("https://teknodeneyim.com/stocks/setselltarget", {
                                            "name": stock_name, "target": 0, "prevTarget": float(sellTarget)})

                except:
                    pass


def result(event, context):
    stocks, data = utils.get_my_stocks()
    my_tickers_target_analysis(stocks, data)

    return {
        'statusCode': 200,
    }
