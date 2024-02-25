#!/usr/bin/python
import bitget.v1.mix.order_api as maxOrderApi
from bitget.bitget_api import BitgetApi

from bitget.exceptions import BitgetAPIException

if __name__ == '__main__':
    apiKey = 'bg_aa2d6e1212aff23224316cbecb996a94'
    secretKey = '15ec828c44dabc9f9e9db4a38b3d02ea08da898d516ba497a7d907297e0803d3'
    passphrase = 'b1TG3TTH3T2Y'

    # Create an instance of the BitgetApi class
    baseApi = BitgetApi(apiKey, secretKey, passphrase)



    # Demo 1:place order
    # maxOrderApi = maxOrderApi.OrderApi(apiKey, secretKey, passphrase)
    # try:
    #     params = {}
    #     params["symbol"] = "BTCUSDT_UMCBL"
    #     params["marginCoin"] = "USDT"
    #     params["side"] = "open_long"
    #     params["orderType"] = "limit"
    #     params["price"] = "27012"
    #     params["size"] = "0.01"
    #     params["timInForceValue"] = "normal"
    #     response = maxOrderApi.placeOrder(params)
    #     print(response)
    # except BitgetAPIException as e:
    #     print("error:" + e.message)

    # try:
    #     params = {}
    #     params["symbol"] = "ATOMUSDT_UMCBL"
    #     params["marginCoin"] = "USDT"
    #     params["side"] = "open_long"
    #     params["orderType"] = "market"
    #     params["size"] = "10"
    #     params["timInForceValue"] = "normal"
    #     response = maxOrderApi.placeOrder(params)
    #     print(response)
    # except BitgetAPIException as e:
    #     print("error:" + e.message)

    # # Demo 2:place order by post directly
    # baseApi = baseApi.BitgetApi(apiKey, secretKey, passphrase)
    # try:
    #     params = {}
    #     params["symbol"] = "BTCUSDT_UMCBL"
    #     params["marginCoin"] = "USDT"
    #     params["side"] = "open_long"
    #     params["orderType"] = "limit"
    #     params["price"] = "27012"
    #     params["size"] = "0.01"
    #     params["timInForceValue"] = "normal"
    #     response = baseApi.post("/api/mix/v1/order/placeOrder", params)
    #     print(response)
    # except BitgetAPIException as e:
    #     print("error:" + e.message)

    # Demo 3:send get request
    try:
        params = {}
        params["productType"] = "umcbl"
        response = baseApi.get("/api/mix/v1/market/contracts", params)
        print(response)
    except BitgetAPIException as e:
        print("error:" + e.message)

    # # Demo 4:send get request with no params
    # try:
    #     response = baseApi.get("/api/spot/v1/account/getInfo", {})
    #     print(response)
    # except BitgetAPIException as e:
    #     print("error:" + e.message)

    # # Demo 5:send get request
    # try:
    #     params = {}
    #     params["symbol"] = "AIUSDT"
    #     params["businessType"] = "spot"
    #     response = baseApi.get("/api/v2/common/trade-rate", params)
    #     print(response)
    # except BitgetAPIException as e:
    #     print("error:" + e.message)