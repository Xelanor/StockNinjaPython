import requests
from datetime import datetime, timedelta
import json
from statistics import mean
import pprint

data_scope = 90

pp = pprint.PrettyPrinter(indent=4)

def epoch_to_date(date):
    return (datetime.fromtimestamp(date) + timedelta(hours=3)).strftime("%d-%m-%Y %H:%M")

def calculate_rsi(data):
    upmoves = []
    downmoves = []
    for i in range(len(data) - 1):
        diff = data[i+1] - data[i]
        if diff > 0:
            upmoves.append(diff)
            downmoves.append(0)
        elif diff < 0:
            upmoves.append(0)
            downmoves.append(diff * -1)
        else:
            upmoves.append(0)
            downmoves.append(0)

    return mean(upmoves), mean(downmoves)

def calculate_env(data):
    data_avg = mean(data)
    
    upper = data_avg + (data_avg * 0.025)
    lower = data_avg - (data_avg * 0.025)
    
    return upper, lower

def calculate_ninja_index(data):
    prev = 0

    result = []
    for i in range(0, len(data)-1):
        try:
            current = (data[i+1] - data[i]) / data[i]

            if current == 0:
                result.append(prev)
            elif (current > 0 and prev > 0) or (current < 0 and prev < 0):
                current += prev
                result.append(current)
            else:
                result.append(current)
            prev = current
        except:
            pass

    return result

def calculate_graph_data(stock, current_price):
    if stock == "XU100.IS":
        url = "https://query1.finance.yahoo.com/v7/finance/chart/XU100.IS?range=30d&interval=1h&indicators=quote&includeTimestamps=false"
        res = requests.get(url)
        stocks_data = res.json()
        closes = stocks_data["chart"]["result"][0]['indicators']["quote"][0]['close']
        #closes.append(current_price)
        #closes = closes[1::8]
        rsi_values = []
        
        env_values = {"upper": [], "lower": []}
        
        for i in range(0,len(closes)):
            env_data = closes[i:i+20]
            upper, lower = calculate_env(env_data)
            env_values["upper"].append(upper)
            env_values["lower"].append(lower)
        
        ninja_data = calculate_ninja_index(closes)
        
        return rsi_values, env_values, ninja_data, closes
    
    url = "https://query1.finance.yahoo.com/v7/finance/chart/{}?range={}d&interval=1d&indicators=quote&includeTimestamps=false".format(stock, data_scope+14)
    res = requests.get(url)
    stocks_data = res.json()
    closes = stocks_data["chart"]["result"][0]['indicators']["quote"][0]['close']
    #.append(current_price)
    #closes = closes[1:]
    rsi_values = []
    env_values = {"upper": [], "lower": []}
    
    for i in range(0,data_scope):
        try:
            rsi_data = closes[i:i+15]
            AvgU, AvgD = calculate_rsi(rsi_data)
            RS = AvgU / AvgD
            RSI = (100 - 100 / ( 1 + RS))
            rsi_values.append(RSI)

            env_data = closes[i:i+20]
            upper, lower = calculate_env(env_data)
            env_values["upper"].append(upper)
            env_values["lower"].append(lower)
        except:
            pass
    
    ninja_data = calculate_ninja_index(closes)
    closes = closes[-data_scope:]
    
    return rsi_values, env_values, ninja_data, closes

def get_stock_target(stock):
    res = requests.get("https://teknodeneyim.com/stocks/single/" + stock)
    data = res.json()
    
    return data

def stock_info(stock, target_dict):
    QUERY_URL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols={}"
    res = requests.get(QUERY_URL.format(stock))
    data_dict = res.json()["quoteResponse"]["result"][0]
    
    result = {
                "name": stock,
                "date": epoch_to_date(data_dict["regularMarketTime"]),
                "price": data_dict["regularMarketPrice"],
                "shortName": data_dict["shortName"],
                "open": data_dict["regularMarketOpen"],
                "dayLow": data_dict["regularMarketDayLow"],
                "volume": data_dict["regularMarketVolume"],
                "dayHigh": data_dict["regularMarketDayHigh"],
                "50avg": data_dict["fiftyDayAverage"],
                "50avgChange": data_dict["fiftyDayAverageChange"],
                "50avgChangePerc": data_dict["fiftyDayAverageChangePercent"],
                "200avg": data_dict["twoHundredDayAverage"],
                "200avgChange": data_dict["twoHundredDayAverageChange"],
                "200avgChangePerc": data_dict["twoHundredDayAverageChangePercent"],
                "dayRange": data_dict["regularMarketDayRange"],
                "prevClose": data_dict["regularMarketPreviousClose"],
                "52wLow": data_dict["fiftyTwoWeekLow"],
                "52wHigh": data_dict["fiftyTwoWeekHigh"],
                "sellTarget" : target_dict['sellTarget'] if 'sellTarget' in target_dict else 0,
                "buyTarget" : target_dict['buyTarget'] if 'buyTarget' in target_dict else 0,
                "prevSellTarget" : target_dict['prevSellTarget'] if 'prevSellTarget' in target_dict else 0,
                "prevBuyTarget" : target_dict['prevBuyTarget'] if 'prevBuyTarget' in target_dict else 0,
                "stateBuy" : target_dict['stateBuy'] if 'stateBuy' in target_dict else False,
                "stateSell" : target_dict['stateSell'] if 'stateSell' in target_dict else False,
            }
    
    return result
    
    
def result(event, context):
    stock = event["queryStringParameters"]["stock"]
    #stock = "THYAO.IS"
    stock_data = get_stock_target(stock)
    targets = stock_info(stock, stock_data)
    
    rsi, env, ninja_data, closes = calculate_graph_data(stock, targets['price'])
    targets['rsi'] = rsi
    targets['env'] = env
    targets['ninja_index'] = ninja_data
    targets['closes'] = closes
    
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type, authorization",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': json.dumps(targets)
    }