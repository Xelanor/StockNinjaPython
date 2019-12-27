import requests
from datetime import datetime, timedelta
import json
from statistics import mean


class StockDetails:
    def __init__(self, stockName, data_scope):
        self.stockName = stockName
        self.data_scope = data_scope
        self.non_stocks = ["XU100.IS", "GC=F"]

    def epoch_to_date(self, date):
        return (datetime.fromtimestamp(date) + timedelta(hours=3)).strftime("%d-%m-%Y %H:%M")

    def get_stock_target(self):
        """
        Get stock target from database
        @return dict {id, name, buyTarget, sellTarget, prevBuyTarget, prevSellTarget}
        """
        QUERY_URL = "https://teknodeneyim.com/stocks/single/{}"
        res = requests.get(QUERY_URL.format(self.stockName))
        data = res.json()

        if data == None:
            self.stock_target = {}
        else: 
            self.stock_target = data

    def get_daily_data(self):
        """
        Get stocks daily data
        @return dict
        """
        QUERY_URL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols={}"
        res = requests.get(QUERY_URL.format(self.stockName))
        data = res.json()["quoteResponse"]["result"]

        self.daily_data = data[0]

        return data

    def get_stock_historic_data(self):
        """
        Get stocks historic data
        Closes for stocks for X period of day. Additional Y day is needed for RSI calculation
        @return dict
        """
        QUERY_URL = "https://query1.finance.yahoo.com/v7/finance/chart/{}?range={}d&interval=1d&indicators=quote&includeTimestamps=false"
        res = requests.get(QUERY_URL.format(self.stockName, self.data_scope + 30))
        data = res.json()["chart"]["result"][0]['indicators']["quote"][0]['close']

        self.historic_data = data

    def get_non_stock_historic_data(self):
        """
        Get non-stocks historic data. Ex: GOLD
        Closes for non-stocks for X period of hours. Multiplication with 8 is to get data_scope days.
        @return dict
        """
        QUERY_URL = "https://query1.finance.yahoo.com/v7/finance/chart/{}?range={}d&interval=1h&indicators=quote&includeTimestamps=false"
        res = requests.get(QUERY_URL.format(
            self.stockName, (self.data_scope) + 30 ))  # Control 8 is true?
        data = res.json()["chart"]["result"][0]['indicators']["quote"][0]['close']
        data = data[::8]
        
        for i in range(len(data)):
            if data[i] == None:
                data[i] = data[i-1]

        self.historic_data = data

    def combine_data_target(self):
        daily_data = self.daily_data
        stock_target = self.stock_target
        stock_details = {
                            "name": self.stockName,
                            "date": self.epoch_to_date(daily_data["regularMarketTime"]),
                            "price": daily_data["regularMarketPrice"],
                            "shortName": daily_data["shortName"],
                            "open": daily_data["regularMarketOpen"],
                            "dayLow": daily_data["regularMarketDayLow"],
                            "volume": daily_data["regularMarketVolume"],
                            "dayHigh": daily_data["regularMarketDayHigh"],
                            "50avg": daily_data["fiftyDayAverage"],
                            "50avgChange": daily_data["fiftyDayAverageChange"],
                            "50avgChangePerc": daily_data["fiftyDayAverageChangePercent"],
                            "200avg": daily_data["twoHundredDayAverage"],
                            "200avgChange": daily_data["twoHundredDayAverageChange"],
                            "200avgChangePerc": daily_data["twoHundredDayAverageChangePercent"],
                            "dayRange": daily_data["regularMarketDayRange"],
                            "prevClose": daily_data["regularMarketPreviousClose"],
                            "52wLow": daily_data["fiftyTwoWeekLow"],
                            "52wHigh": daily_data["fiftyTwoWeekHigh"],
                            "sellTarget": stock_target['sellTarget'] if 'sellTarget' in stock_target else 0,
                            "buyTarget": stock_target['buyTarget'] if 'buyTarget' in stock_target else 0,
                            "prevSellTarget": stock_target['prevSellTarget'] if 'prevSellTarget' in stock_target else 0,
                            "prevBuyTarget": stock_target['prevBuyTarget'] if 'prevBuyTarget' in stock_target else 0,
                            "stateBuy": stock_target['stateBuy'] if 'stateBuy' in stock_target else False,
                            "stateSell": stock_target['stateSell'] if 'stateSell' in stock_target else False,
                            "rsi": self.rsi_values,
                            "env": self.env_values,
                            "ninja_index": self.ninja_values,
                            "ninja_index_s": self.ninja_values_s,
                            "triple_index": self.triple_index_values,
                            "closes": self.historic_data[-self.data_scope:]
                        }

        self.stock_details = stock_details

    def calculate_rsi_index(self):
        """
        Calculation of RSI index
        """
        rsi_values = []
        historic_data = self.historic_data[-1 * (self.data_scope + 14):]
        for i in range(0, self.data_scope):
            upmoves = []
            downmoves = []
            rsi_closes = historic_data[i:i+15]

            for i in range(len(rsi_closes) - 1):
                diff = rsi_closes[i+1] - rsi_closes[i]
                if diff > 0:
                    upmoves.append(diff)
                elif diff < 0:
                    downmoves.append(diff * -1)

            AvgU = sum(upmoves) / 14
            AvgD = sum(downmoves) / 14
            try:
                RS = AvgU / AvgD
            except ZeroDivisionError:
                RS = 100
                
            RSI = (100 - 100 / (1 + RS))
            rsi_values.append(RSI)

        self.rsi_values = rsi_values
        return rsi_values

    def calculate_env_index(self):
        historic_data = self.historic_data[-1 * (self.data_scope + 20):]

        env_values = {"upper": [], "lower": []}

        for i in range(0, self.data_scope):
            try:
                env_data = historic_data[i:i+21]

                data_avg = mean(env_data)
                upper = data_avg + (data_avg * 0.025)
                lower = data_avg - (data_avg * 0.025)

                env_values["upper"].append(upper)
                env_values["lower"].append(lower)
            except:
                pass

        self.env_values = env_values
        return env_values
        
    def calculate_ninja_index(self):
        historic_data = self.historic_data[-1 * (self.data_scope + 1):]
        prev = 0
        ninja_values = []
        for i in range(0, len(historic_data)-1):
            try:
                current = (historic_data[i+1] - historic_data[i]) / historic_data[i]
                
                if current == 0:
                    ninja_values.append(prev)
                elif (current > 0 and prev > 0) or (current < 0 and prev < 0):
                    current += prev
                    ninja_values.append(current)
                else:
                    ninja_values.append(current)
                prev = current
            except:
                pass

        self.ninja_values = ninja_values
        return ninja_values

    def calculate_ninja_index_s(self):
        historic_data = self.historic_data[-1 * (self.data_scope + 1):]
        prev = 0
        ninja_values = []
        for i in range(0, len(historic_data)-1):
            try:
                current = (historic_data[i+1] - historic_data[i]) / historic_data[i]
                
                if current == 0:
                    ninja_values.append(prev)
                elif (current > 0 and prev > 0) or (current < 0 and prev < 0):
                    current += prev
                    ninja_values.append(current)
                else:
                    current += prev
                    ninja_values.append(current)
                prev = current
            except:
                pass

        self.ninja_values_s = ninja_values
        return ninja_values
        
    def calculate_triple_index(self):
        first_data = self.historic_data[-1 * (self.data_scope + 30):]
        second_data = self.historic_data[-1 * (self.data_scope + 14):]
        third_data = self.historic_data[-1 * (self.data_scope + 7):]

        triple_index_values = {"first_list": [], "second_list": [], "third_list": []}

        for i in range(0, self.data_scope):
            try:
                triple_index_values["first_list"].append(mean(first_data[i:i+30]))
                triple_index_values["second_list"].append(mean(second_data[i:i+14]))
                triple_index_values["third_list"].append(mean(third_data[i:i+7]))
            except:
                pass
        
        self.triple_index_values = triple_index_values
        return triple_index_values
    
    def start(self):
        """
        Main entry point to get stock details
        Fetch the targets, get daily data, combine these two
        Get historic data for stock or non-stock
        """
        self.get_stock_target()
        self.get_daily_data()

        if self.stockName in self.non_stocks:
            self.get_non_stock_historic_data()
            self.rsi_values = []
        else:
            self.get_stock_historic_data()
            self.calculate_rsi_index()

        self.calculate_env_index()
        self.calculate_ninja_index()
        self.calculate_ninja_index_s()
        self.calculate_triple_index()
        self.combine_data_target()

        from pprint import pprint
        pprint(self.stock_details)

# details = StockDetails("XU100.IS", 90)
# details.start()