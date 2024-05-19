import pandas as pd
import numpy as np
import time

import bitget.v1.mix.order_api as maxOrderApi
import bitget.v1.mix.market_api as maxMarketApi
from bitget.bitget_api import BitgetApi
from bitget.exceptions import BitgetAPIException

from decouple import config
from get_time import get_unix_times
from constants import MARKETS



apiKey = config('apiKey')
secretKey = config('secretKey')
passphrase = config('passphrase')

# Create an instance of the BitgetApi class
baseApi = BitgetApi(apiKey, secretKey, passphrase)

markets = MARKETS
# Send get request
# try:
#     params = {}
#     params["symbol"] = markets[0]
#     params["productType"] = "USDT-FUTURES"
#     params["granularity"] = "1H"
#     print(params)
#     response = baseApi.get("/api/v2/mix/market/history-candles", params)
#     df = pd.DataFrame(response)
#     df['time'] = df['data'].apply(lambda x: x[0])
#     df['time'] = pd.to_numeric(df['time'])
#     df['time'] = pd.to_datetime(df['time'], unit='ms')
#     df['BTCUSDT'] = df['data'].apply(lambda x: x[4])
#     df = df.drop(['code', 'msg', 'requestTime', 'data'], axis=1)
#     df.to_csv('data.csv', index=False)
# except BitgetAPIException as e:
#     print("error:" + e.message)




# Get current time and create times dict to collect multiple batches of data from the API
# times_dict = get_unix_times()



def fetch_and_compile_candle_data(times_dict, markets, granularity):
    try:
        final_df = pd.DataFrame()
        for market in markets:
            interim_df = pd.DataFrame() # Reset interim_df for each market
            for times_key, times_value in times_dict.items():
                params = {
                    "symbol": market,
                    "productType": "USDT-FUTURES",
                    "granularity": granularity,
                    "endTime": times_value["to_unix"],
                    "limit": "200"
                }
                response = baseApi.get("/api/v2/mix/market/history-candles", params)
            
                # Temporary DataFrame from the response
                temp_df = pd.DataFrame(response)
                
                # Process the 'time' column
                temp_df['time'] = temp_df['data'].apply(lambda x: x[0])
                temp_df['time'] = pd.to_numeric(temp_df['time'])
                temp_df['time'] = pd.to_datetime(temp_df['time'], unit='ms')

                # Append the data for the current market
                interim_df = pd.concat([interim_df, temp_df], ignore_index=True, axis=0)
                
                # Create a new column for the market using the exit price (assuming index 4 is the exit price)
            final_df[market] = interim_df['data'].apply(lambda x: x[4])

            # Sleep to avoid hitting the rate limit
            time.sleep(0.2)  
            
            # Ensure the 'time' column is synchronized across all market columns
            if 'time' not in final_df.columns:
                final_df['time'] = interim_df['time']

            
        # Sort the times in the DataFrame in ascending order
        final_df.sort_values(by='time', inplace=True)

        # Reorder the DataFrame columns to have 'time' as the first column
        cols = ['time'] + [col for col in final_df.columns if col != 'time']
        df_market_prices = final_df[cols]
        
        # Export the compiled data to a CSV file
        df_market_prices.to_csv(f"data_{granularity}.csv", index=False)

    except BitgetAPIException as e:
        print(f"error: {e.message}")



# def fetch_and_compile_candle_data(times_dict, markets, filepath='data_15m.csv'):
#     final_df = pd.DataFrame()
#     for market in markets:
#         interim_df = pd.DataFrame()  # Reset interim_df for each market
#         for times_key, times_value in times_dict.items():
#             params = {
#                 "symbol": market,
#                 "productType": "USDT-FUTURES",
#                 "granularity": "15m",
#                 "endTime": times_value["to_unix"],
#                 "limit": "200"
#             }
#             print(params)
#             try:
#                 response = baseApi.get("/api/v2/mix/market/history-candles", params)
#             except BitgetAPIException as e:
#                 print(f"Error fetching data for market {market}: {e.message}")
#                 continue

#             # Assume response is structured correctly and directly usable; adjust if needed
#             temp_df = pd.DataFrame(response)
#             temp_df['time'] = temp_df['data'].apply(lambda x: x[0])
#             temp_df['time'] = pd.to_numeric(temp_df['time'])
#             temp_df['time'] = pd.to_datetime(temp_df['time'], unit='ms')
#             interim_df = pd.concat([interim_df, temp_df], ignore_index=True)

#         if not interim_df.empty:
#             final_df[market] = interim_df['data'].apply(lambda x: x[4])
#             if 'time' not in final_df.columns:
#                 final_df['time'] = interim_df['time']

#     final_df.sort_values(by='time', inplace=True)
#     cols = ['time'] + [col for col in final_df.columns if col != 'time']
#     final_df = final_df[cols]

#     # Check if the file exists and append if it does, else create a new file
#     file_exists = os.path.isfile(filepath)
#     with open(filepath, 'a' if file_exists else 'w', newline='') as f:
#         final_df.to_csv(f, index=False, header=not file_exists)

# # Example usage
# times_dict = {
#     # Your times_dict content here
# }
# markets = [
#     # Your list of market symbols here
# ]

# # Fetch and compile the candle data, appending to 'data_15m.csv'
# fetch_and_compile_candle_data(times_dict, markets)

