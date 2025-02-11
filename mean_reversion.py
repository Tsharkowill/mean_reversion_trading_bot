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

# Function to log the order response
def log_order_response(response, file_path):

    try:
        # Load existing data if the file exists
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []

        # Append the new response data
        data.append(response)

        # Write updated data back to the file
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Order logged successfully: {response['data']['orderId']}")
    except Exception as e:
        print(f"Failed to log order: {e}")

def calculate_zscore(market, spreads_df, WINDOW):
    spread_series = spreads_df[market]
    mean = spread_series.rolling(window=WINDOW).mean()
    std = spread_series.rolling(window=WINDOW).std()
    spreads_df[f'z_score_{market}'] = (spread_series - mean) / std

def calculate_limit_percentage(cadence):
    # Adjust this function to dynamically set the percentage based on cadence
    # For example:
    if cadence == 'high':
        return 0.05  # 5% for high cadence data
    elif cadence == 'medium':
        return 0.1  # 10% for medium cadence data
    else:
        return 0.15  # 15% for low cadence data


def manage_trade(price_data_file, MARKETS, cadence, Z_SCORE, WINDOW):
    
    price_data = pd.read_csv(price_data_file)

    try:
        with open(f'open_trades_{cadence}.json', 'r') as json_file:
            open_trades = json.load(json_file)
        print(f'Open positions loaded: {open_trades}')
    except FileNotFoundError:
        open_trades = {}
        print('No open positions found, starting fresh')

    keys_to_remove = []
    limit_percentage = calculate_limit_percentage(cadence)

    for market in MARKETS:
       
        calculate_zscore(market, price_data, WINDOW)
        z_score_column = f'z_score_{market}'
        current_z_score = price_data[z_score_column].iloc[-1]
        print(current_z_score)
        key_to_remove = None

        if market not in open_trades:
            if current_z_score <= -Z_SCORE:
                enter_market_trade(market, "long", price_data, open_trades)
                enter_limit_trade(market, "long", price_data, limit_percentage)
            elif current_z_score >= Z_SCORE:
                enter_market_trade(market, "short", price_data, open_trades)
                enter_limit_trade(market, "short", price_data, limit_percentage)


        elif market in open_trades:
            position_type = open_trades[market]['position_type']
            if position_type == "long" and current_z_score >= Z_SCORE:
                key_to_remove = market

            elif position_type == "short" and current_z_score <= -Z_SCORE:
                key_to_remove = market
        
            if key_to_remove is not None:
                keys_to_remove.append(key_to_remove) 

    for key in keys_to_remove:
        del open_trades[key]


    with open(f'open_trades_{cadence}.json', 'w') as json_file:
        json.dump(open_trades, json_file, indent=4)


def enter_market_trade(market, position_type, price_data, open_trades):

    asset_latest_price = price_data[market].iloc[-1]

    asset_position_size = round(TRADE_SIZE / asset_latest_price, 2)

    if position_type == "long":
        print(f"Opening long trade on: {market}")
        params = {
            "symbol": f"{market}_UMCBL",
            "marginCoin": "USDT",
            "side": "open_long",
            "orderType": "market",
            "size": asset_position_size,
            "timeInForceValue": "normal"
        }

    elif position_type == "short":
        print(f"Opening short trade on: {market}")
        params = {
            "symbol": f"{market}_UMCBL",
            "marginCoin": "USDT",
            "side": "open_short",
            "orderType": "market",
            "size": asset_position_size,
            "timeInForceValue": "normal"
        }

    # Execute the trades
    order_api = maxOrderApi.OrderApi(apiKey, secretKey, passphrase)
    # File to store order responses
    ORDER_FILE = "order_responses.json"
    try:
        response_base = order_api.placeOrder(params)
        print(response_base)
        # Check if the response is successful
        if response_base['code'] == '00000':
            log_order_response(response_base, ORDER_FILE)
        else:
            error_message = f"Order failed: {response_base['msg']}"
            print(error_message)
    except BitgetAPIException as e:
        print("error:" + e.message)

    # Save opened positions
    open_trades[f"{market}"] = {
        "position_type": position_type,
        "base_position_size": asset_position_size
    }



def enter_limit_trade(market, position_type, price_data, limit_percentage):

    asset_latest_price = price_data[market].iloc[-1]

    asset_position_size = round(TRADE_SIZE / asset_latest_price, 2)

    if position_type == "long":
        limit_price = asset_latest_price * (1 + limit_percentage)
        print(f"Opening long limit trade on: {market}")
        params = {
            "symbol": f"{market}_UMCBL",
            "marginCoin": "USDT",
            "side": "close_long",
            "orderType": "limit",
            "size": asset_position_size,
            "price": limit_price,
            "timeInForceValue": "normal"
        }

    elif position_type == "short":
        limit_price = asset_latest_price * (1 - limit_percentage)
        print(f"Opening short trade on: {market}")
        params = {
            "symbol": f"{market}_UMCBL",
            "marginCoin": "USDT",
            "side": "close_short",
            "orderType": "limit",
            "size": asset_position_size,
            "price": limit_price,
            "timeInForceValue": "normal"
        }

    # Execute the trades
    order_api = maxOrderApi.OrderApi(apiKey, secretKey, passphrase)
    # File to store order responses
    ORDER_FILE = "order_responses.json"
    try:
        response_base = order_api.placeOrder(params)
        print(response_base)
        # Check if the response is successful
        if response_base['code'] == '00000':
            log_order_response(response_base, ORDER_FILE)
        else:
            error_message = f"Order failed: {response_base['msg']}"
            print(error_message)
    except BitgetAPIException as e:
        print("error:" + e.message)
