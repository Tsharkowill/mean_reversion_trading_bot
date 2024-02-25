import pandas as pd
import numpy as np
import json

import bitget.v1.mix.order_api as maxOrderApi
import bitget.v1.mix.market_api as maxMarketApi
from bitget.bitget_api import BitgetApi
from bitget.exceptions import BitgetAPIException

from decouple import config
from functions import to_unix_milliseconds, get_unix_times

if __name__ == '__main__':

    apiKey = config('apiKey')
    secretKey = config('secretKey')
    passphrase = config('passphrase')

    # Create an instance of the BitgetApi class
    baseApi = BitgetApi(apiKey, secretKey, passphrase)

# Maybe make list of market pairs to get data for and create a for loop to iterate through, appending on to the same csv
# Make ["symbol"] and iterable
# Also use the get_unix_times function to grab more data for each trading pair finally append each new pair as
# a new column on to the data frame
# afterwards the csv will be used to find cointegrated pairs or maybe it just remains a dataframe then coint pairs are the csv
# 20 requests per second is the rate limit
    
    # cancel crave
    # cancel netflix
    # maybe use vpn to start getting some movies downloaded
    
    markets = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "EOSUSDT", "BCHUSDT", "LTCUSDT", "ADAUSDT", "ETCUSDT", "LINKUSDT", "DOGEUSDT", "SOLUSDT", "MATICUSDT", "BNBUSDT", "UNIUSDT", "ICPUSDT", "AAVEUSDT", "XLMUSDT", "ATOMUSDT", "XTZUSDT", "SUSHIUSDT", "AXSUSDT", "THETAUSDT", "AVAXUSDT", "SHIBUSDT", "MANAUSDT", "GALAUSDT", "SANDUSDT", "DYDXUSDT", "CRVUSDT"]

# Send get request
    try:
        params = {}
        params["symbol"] = markets[0]
        params["productType"] = "USDT-FUTURES"
        params["granularity"] = "1H"
        print(params)
        response = baseApi.get("/api/v2/mix/market/history-candles", params)
        df = pd.DataFrame(response)
        df['time'] = df['data'].apply(lambda x: x[0])
        df['time'] = pd.to_numeric(df['time'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        df['BTCUSDT'] = df['data'].apply(lambda x: x[4])
        df = df.drop(['code', 'msg', 'requestTime', 'data'], axis=1)
        df.to_csv('data.csv', index=False)
    except BitgetAPIException as e:
        print("error:" + e.message)

