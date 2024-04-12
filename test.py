import pandas as pd
import time


from bitget.bitget_api import BitgetApi
from bitget.exceptions import BitgetAPIException
from get_markets import fetch_and_compile_candle_data
from get_time import get_unix_times
from constants import MARKETS

from decouple import config
from get_time import get_unix_times
from datetime import datetime, timedelta

apiKey = config('apiKey')
secretKey = config('secretKey')
passphrase = config('passphrase')

# Create an instance of the BitgetApi class
baseApi = BitgetApi(apiKey, secretKey, passphrase)

# Adjusted rounding function for nearest hour
def to_unix_milliseconds_nearest_hour(dt):
    if dt.minute >= 30:  # If past the half-hour mark, round up
        minutes_to_add = 60 - dt.minute
        dt_rounded = dt.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=minutes_to_add)
    else:  # If before the half-hour mark, round down
        dt_rounded = dt.replace(minute=0, second=0, microsecond=0)
    return int(dt_rounded.timestamp() * 1000)

def get_unix_times_hours(intervals):
    # Get current datetime and round to the nearest hour
    current_time = datetime.now()
    current_time_rounded = current_time - timedelta(minutes=current_time.minute, seconds=current_time.second, microseconds=current_time.microsecond)
    if current_time.minute >= 30:  # Adjust to round to nearest hour rather than truncating
        current_time_rounded += timedelta(hours=1)
    
    # Initialize the dictionary to store time ranges
    times_dict = {}
    intervals_step = 200  # Define the number of hour intervals to step back for each range.
    
    # Generate sequential time ranges
    for i in range(1, intervals):
        end_time = current_time_rounded - timedelta(hours=(i-1) * intervals_step)
        start_time = current_time_rounded - timedelta(hours=i * intervals_step)
        
        times_dict[f"range_{i}"] = {
            "from_unix": to_unix_milliseconds_nearest_hour(start_time),
            "to_unix": to_unix_milliseconds_nearest_hour(end_time),
        }
    
    return times_dict


def fetch_and_compile_hour_candles(times_dict, markets):
    try:
        final_df = pd.DataFrame()
        for market in markets:
            interim_df = pd.DataFrame() # Reset interim_df for each market
            for times_key, times_value in times_dict.items():
                params = {
                    "symbol": market,
                    "productType": "USDT-FUTURES",
                    "granularity": "1H",
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
            time.sleep(0.3)  
            
            # Ensure the 'time' column is synchronized across all market columns
            if 'time' not in final_df.columns:
                final_df['time'] = interim_df['time']

            
        # Sort the times in the DataFrame in ascending order
        final_df.sort_values(by='time', inplace=True)

        # Reorder the DataFrame columns to have 'time' as the first column
        cols = ['time'] + [col for col in final_df.columns if col != 'time']
        df_market_prices = final_df[cols]
        
        # Export the compiled data to a CSV file
        df_market_prices.to_csv('data_1h.csv', index=False)

    except BitgetAPIException as e:
        print(f"error: {e.message}")


# times_dict = get_unix_times_hours(20)
# fetch_and_compile_hour_candles(times_dict, MARKETS)

times_dict = get_unix_times()
fetch_and_compile_candle_data(times_dict, MARKETS)
