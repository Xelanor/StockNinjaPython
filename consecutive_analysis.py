import requests
from datetime import datetime, timedelta

from constants.tickers import valuable_tickers
import json
import utils

DAYS_BEFORE_ALL_STOCKS = 5
DAYS_BEFORE_MY_STOCKS = 3


def calculate_consecutive_days(data):

    data = data[::-1]

    first_event = data[0] - data[1]  # If positive increasing else decreasing
    first_event = True if first_event >= 0 else False

    days = 1

    for i in range(1, len(data) - 1):
        event = True if data[i] - data[i + 1] >= 0 else False

        if event == first_event:
            days += 1
        else:
            break

    return days, first_event


def calculate_rate(data, days):
    rate = (data[-1] - data[-1 * (days + 1)]) / data[-1]
    return rate


def bottom_analysis():

    my_stocks, _ = utils.get_my_stocks()
    all_stocks = valuable_tickers

    for stockName in all_stocks:
        days_before = DAYS_BEFORE_MY_STOCKS if stockName in my_stocks else DAYS_BEFORE_ALL_STOCKS
        closes = utils.get_stock_historic_data(stockName, 1)[-1 * 10:]
        days, state = calculate_consecutive_days(closes)

        rate = str(round(calculate_rate(closes, days) * 100, 2))

        if state and days >= days_before and stockName in my_stocks:
            utils.telegram_bot_sendtext("{} {} gündür yükselişte bir göz at \n% {} (Senin Hissen).".format(
                stockName[:-3], days, rate))
        elif not state and days >= days_before and stockName in my_stocks:
            utils.telegram_bot_sendtext("{} {} gündür düşüşte almayı değerlendirebilirsin \n% {} (Senin Hissen).".format(
                stockName[:-3], days, rate))
        elif not state and days >= days_before:
            utils.telegram_bot_sendtext("{} {} gündür düşüşte almayı değerlendirebilirsin \n% {} (Genel Liste).".format(
                stockName[:-3], days, rate))


def result(event, context):
    bottom_analysis()

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type, authorization",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': json.dumps("success")
    }


if __name__ == '__main__':
    output = result("", "")
    print(output["body"])
