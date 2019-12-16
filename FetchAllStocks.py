from constants.tickers import tickers
from StockDetails import StockDetails
import json


def rateCalculator(price, prevClose):
    rate = (((price - prevClose) / prevClose) * 100)
    rate = round(rate, 2)
    return rate


def fetch_all_stocks():
    result = []
    stock_names = ",".join(tickers)
    details = StockDetails(stock_names, 1)

    stocks_data = details.get_daily_data()

    for data_dict in stocks_data:
        price = data_dict["regularMarketPrice"]
        prevClose = data_dict["regularMarketPreviousClose"]

        rate = rateCalculator(price, prevClose)
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

    return result


print(fetch_all_stocks())
