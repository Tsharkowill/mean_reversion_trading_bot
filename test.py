import pandas as pd
import json


from constants import TRADE_SIZE
import bitget.v1.mix.order_api as maxOrderApi
from bitget.bitget_api import BitgetApi
from bitget.exceptions import BitgetAPIException
from decouple import config

apiKey = config('apiKey')
secretKey = config('secretKey')
passphrase = config('passphrase')

baseApi = BitgetApi(apiKey, secretKey, passphrase)

market_params = {
            "symbol": f"LDOUSDT_UMCBL",
            "marginCoin": "USDT",
            "side": "open_long",
            "orderType": "market",
            "size": 10,
            "timeInForceValue": "normal"
        }

limit_params = {
            "symbol": f"LDOUSDT_UMCBL",
            "marginCoin": "USDT",
            "side": "close_long",
            "orderType": "limit",
            "size": 10,
            "price": 1.85,
            "timeInForceValue": "normal"
        }


# Execute the trades
order_api = maxOrderApi.OrderApi(apiKey, secretKey, passphrase)

response_base = order_api.placeOrder(market_params)
print(response_base)

response_base = order_api.placeOrder(limit_params)
print(response_base)