from constants.tickers import tickers
import json
import utils


def fetch_all_stocks():
    result = []
    stock_names = ",".join(tickers)

    stocks_data = utils.get_current_tickers_data(stock_names)
    negative = 0
    total = 0

    for data_dict in stocks_data:
        price = data_dict["regularMarketPrice"]
        prevClose = data_dict["regularMarketPreviousClose"]

        rate = utils.rateCalculator(price, prevClose)
        negative += 1 if rate < 0 else 0
        total += 1

        try:
            stock_name = data_dict["symbol"]

            stock_dict = {
                "stockName": stock_name,
                "price": price,
                "dayRange": data_dict["regularMarketDayRange"],
                "rate": rate
            }

            result.append(stock_dict)
        except:
            pass

    result.append(negative)
    result.append(total)
    return result


def result(event, context):
    prices = fetch_all_stocks()

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type, authorization",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': json.dumps(prices)
    }


if __name__ == '__main__':
    output = result("", "")
    print(output["body"])
