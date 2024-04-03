import pandas as pd
import time
import os
import glob

from get_time import get_unix_times
from get_markets import fetch_and_compile_candle_data
from cointegration import update_hedge_ratios
from trade_functions import calculate_spread, manage_close_only_trades
from data_functions import append_filtered_data, filter_and_append_data, merge_json
from constants import MARKETS

from bitget.bitget_api import BitgetApi
from decouple import config

'''Create instance of Api'''

apiKey = config('apiKey')
secretKey = config('secretKey')
passphrase = config('passphrase')

baseApi = BitgetApi(apiKey, secretKey, passphrase)



merge_json('open_positions.json', 'close_only.json')

append_filtered_data('spreads_df.csv', 'closing_spreads_df.csv', 'close_only.json')

filter_and_append_data('cointegrated_pairs.csv', 'cointegrated_close.csv', 'close_only.json')

pattern = '*simulation_train.csv'

files_to_delete = glob.glob(pattern)

for file in files_to_delete:
    try:
        os.remove(file)
        print(f"Deleted {file}")
    except Exception as e:
        print(f"Error deleting {file}: {e}")


while True:

    start_time = time.time()
        
    '''Getting new time data'''

    # Create dictionary for requesting market data
    times_dict = get_unix_times()

    # Get market prices and create a .csv for selected markets
    fetch_and_compile_candle_data(times_dict, MARKETS)

    update_hedge_ratios('data_15m.csv', 'cointegrated_close.csv')

    closing_spreads = calculate_spread('data_15m.csv', 'cointegrated_close.csv')
    if closing_spreads is not None:
        closing_spreads.to_csv('closing_spreads_df', index=False)
    else:
        print('No close only poisitons at this time')

    if closing_spreads is not None:
        manage_close_only_trades('closing_spreads_df.csv', 'close_only.json')
    else:
        print('No close only positions at this time')

    end_time = time.time()
    elapsed_time = end_time - start_time
    sleep_time = max(15*60 - elapsed_time, 0)
    time.sleep(sleep_time)